from DateTime import DateTime
from DocumentTemplate import sequence
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.interfaces import IWorksheet
from bika.lims.utils import TimeOrDate
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from zope.app.component.hooks import getSite
from zope.component import getMultiAdapter
from zope.interface import implements
import plone, json

class WorksheetWorkflowAction(WorkflowAction):
    """ Workflow actions taken in Worksheets
        This function is called to do the worflow actions
        that apply to analyses in worksheets
    """
    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        workflow = getToolByName(self.context, 'portal_workflow')
        pc = getToolByName(self.context, 'portal_catalog')
        rc = getToolByName(self.context, 'reference_catalog')
        originating_url = self.request.get_header("referer",
                                                  self.context.absolute_url())
        skiplist = self.request.get('workflow_skiplist', [])
        action, came_from = WorkflowAction._get_form_workflow_action(self)

        if action == 'submit' and self.request.form.has_key("Result"):
            selected_analyses = WorkflowAction._get_selected_items(self)
            selected_analysis_uids = selected_analyses.keys()
            results = {}

            # first save results for entire form
            for uid, result in self.request.form['Result'][0].items():
                results[uid] = result
                if uid in selected_analyses:
                    analysis = selected_analyses[uid]
                else:
                    analysis = rc.lookupObject(uid)
                service = analysis.getService()
                interims = form["InterimFields"][0][uid]
                analysis.edit(
                    Result = result,
                    InterimFields = json.loads(interims),
                    Retested = form.has_key('retested') and \
                               form['retested'].has_key(uid),
                    Unit = service.getUnit())

            # discover which items may be submitted
            submissable = []
            for uid, analysis in selected_analyses.items():
                analysis = selected_analyses[uid]
                service = analysis.getService()
                # but only if they are selected
                if uid not in selected_analysis_uids:
                    continue
                # and if all their dependencies are at least 'to_be_verified'
                can_submit = True
                for dependency in analysis.getDependencies():
                    if workflow.getInfoFor(dependency, 'review_state') in \
                       ('sample_due', 'sample_received'):
                        can_submit = False
                if can_submit and results[uid]:
                    submissable.append(analysis)

            # and then submit them.
            for analysis in submissable:
                if not analysis.UID() in skiplist:
                    try:
                        workflow.doActionFor(analysis, 'submit')
                    except WorkflowException:
                        pass

            message = _("Changes saved.")
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.response.redirect(originating_url)

        else:
            # default bika_listing.py/WorkflowAction for other transitions
            WorkflowAction.__call__(self)

class WorksheetAddView(BrowserView):
    """ This creates a new Worksheet and redirects to it.
        If a template was selected, the worksheet is pre-populated here.
    """
    def __call__(self):
        form = self.request.form
        rc = getToolByName(self.context, "reference_catalog")
        pc = getToolByName(self.context, "portal_catalog")

        ws_id = self.context.generateUniqueId('Worksheet')
        self.context.invokeFactory(id = ws_id, type_name = 'Worksheet')
        ws = self.context[ws_id]

        # overwrite saved context UID for event subscribers
        self.request['context_uid'] = ws.UID()

        # if no template was specified, redirect to blank worksheet
        if not form.has_key('wstemplate') or not form['wstemplate']:
            ws.processForm()
            self.request.RESPONSE.redirect(ws.absolute_url())

        wst = rc.lookupObject(form['wstemplate'])
        wstlayout = wst.getLayout()
        services = wst.getService()
        service_uids = [s.UID() for s in services]

        count_a = count_b = count_c = count_d = 0
        for row in wstlayout:
            if row['type'] == 'a': count_a = count_a + 1
            if row['type'] == 'b': count_b = count_b + 1
            if row['type'] == 'c': count_c = count_c + 1
            if row['type'] == 'd': count_d = count_d + 1

        selected = {} # ar.id : {analyses,services,uids}
        ars = [] # for keeping track of order of ARs

        # get the oldest analyses first
        for a in pc(portal_type = 'Analysis',
                    getServiceUID = service_uids,
                    review_state = 'sample_received',
                    worksheetanalysis_review_state = 'unassigned',
                    sort_on = 'getDueDate'):
            analysis = a.getObject()
            ar = analysis.aq_parent
            if not selected.has_key(ar.id):
                if len(selected) < count_a:
                    selected[ar.id] = {}
                    selected[ar.id]['analyses'] = []
                    selected[ar.id]['services'] = []
                    ars.append(ar.id)
                else:
                    continue
            selected[ar.id]['analyses'].append(analysis.UID())
            selected[ar.id]['services'].append(analysis.getServiceUID())

        analyses = []
        used_ars = {} # position : {analyses,services,uids}
        for row in wstlayout:
            position = int(row['pos'])
            if row['type'] == 'a':
                if ars:
                    ar = ars.pop(0)
                    used_ars[position] = {}
                    used_ars[position]['ar'] = ar.UID()
                    used_ars[position]['serv'] = selected[ar]['services']
                    for analysis in selected[ar]['analyses']:
                        analyses.append((position, analysis))
            if row['type'] in ['b', 'c']:
                # XXX This doesn't seem to cater for b and c differently
                ## select a reference sample for this slot
                ## a) must be created from the same reference definition selected in ws template
                ## b) takes the sample that handles all (or the most) services.
                reference_definition_uid = row['sub']
                references = {}
                reference_found = False
                for s in pc(portal_type = 'ReferenceSample',
                            review_state = 'current',
                            inactive_state = 'active',
                            getReferenceDefinitionUID = reference_definition_uid):
                    reference = s.getObject()
                    reference_uid = reference.UID()
                    references[reference_uid] = {}
                    references[reference_uid]['services'] = []
                    references[reference_uid]['count'] = 0
                    specs = reference.getResultsRangeDict()
                    for service_uid in service_uids:
                        if specs.has_key(service_uid):
                            references[reference_uid]['services'].append(service_uid)
                            references[reference_uid]['count'] += 1
                    if references[reference_uid]['count'] == len(service_uids):
                        reference_found = True
                        break
                # reference_found this reference has all the services
                if reference_found:
                    ws.assignReference(Reference = reference_uid,
                                       Position = position,
                                       Type = row['type'],
                                       Service = service_uids)
                else:
                    # find the reference with the most services
                    these_services = service_uids
                    reference_keys = references.keys()
                    no_of_services = 0
                    mostest = None
                    for key in reference_keys:
                        if references[key]['count'] > no_of_services:
                            no_of_services = references[key]['count']
                            mostest = key
                    if mostest:
                        ws.assignReference(
                            Reference = mostest,
                            Position = position,
                            Type = row['type'],
                            Service = references[mostest]['services'])
        if analyses:
            ws.assignNumberedAnalyses(analyses)

        if count_d:
            for row in wstlayout:
                if row['type'] == 'd':
                    position = int(row['pos'])
                    dup_pos = int(row['dup'])
                    if used_ars.has_key(dup_pos):
                        ws.assignDuplicate(
                            AR = used_ars[dup_pos]['ar'],
                            Position = position,
                            Service = used_ars[dup_pos]['serv'])
        ws.edit(MaxPositions = len(wstlayout))
        ws.processForm()

        self.request.RESPONSE.redirect(ws.absolute_url())

class WorksheetManageResultsView(AnalysesView):

    def __init__(self, context, request, allow_edit = False, **kwargs):
        super(WorksheetManageResultsView, self).__init__(context, request)
        self.contentFilter = {}
        self.show_select_row = False
        self.show_sort_column = True
        self.allow_edit = True

        self.columns = {
            'Pos': {'title': _('Pos')},
            'Client': {'title': _('Client')},
            'Order': {'title': _('Order')},
            'getRequestID': {'title': _('Request ID')},
            'DueDate': {'title': _('Due Date')},
            'Category': {'title': _('Category')},
            'Service': {'title': _('Analysis')},
            'Result': {'title': _('Result')},
            'Uncertainty': {'title': _('+-')},
            'retested': {'title': _('Retested'), 'type':'boolean'},
            'Attachments': {'title': _('Attachments')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns':['Pos',
                        'Client',
                        'Order',
                        'getRequestID',
                        'DueDate',
                        'Category',
                        'Service',
                        'Result',
                        'Attachments',
                        'state_title'],
             },
        ]

    def folderitems(self):
        self.contentsMethod = self.context.getFolderContents
        items = AnalysesView.folderitems(self)
        pos = 0
        for x, item in enumerate(items):
            obj = item['obj']
            pos += 1
            items[x]['Pos'] = pos
            service = obj.getService()
            items[x]['Category'] = service.getCategory().Title()
            ar = obj.aq_parent
            items[x]['replace']['getRequestID'] = "<a href='%s'>%s</a>" % \
                 (ar.absolute_url(), ar.Title())
            client = ar.aq_parent
            items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % \
                 (client.absolute_url(), client.Title())
            items[x]['DueDate'] = \
                TimeOrDate(obj.getDueDate)
            items[x]['Order'] = hasattr(ar, 'getClientOrderNumber') \
                 and ar.getClientOrderNumber() or ''
            if obj.portal_type == 'DuplicateAnalysis':
                items[x]['after']['Pos'] = '<img width="16" height="16" src="%s/++resource++bika.lims.images/duplicate.png"/>' % \
                    (self.context.absolute_url())
            elif obj.portal_type == 'ReferenceAnalysis':
                if obj.ReferenceType == 'b':
                    items[x]['after'] += '<img width="16" height="16" src="%s/++resource++bika.lims.images/blank.png"/>' % \
                        (self.context.absolute_url())
                else:
                    items[x]['after'] += '<img width="16" height="16" src="%s/++resource++bika.lims.images/control.png"/>' % \
                        (self.context.absolute_url())

        items = sorted(items, key = itemgetter('getRequestID'))

        return items


class WorksheetAddAnalysisView(AnalysesView):
    def __init__(self, context, request):
        super(WorksheetAddAnalysisView, self).__init__(context, request)
        self.content_add_actions = {}
        self.contentFilter = {'portal_type': 'Analysis',
                              'review_state':'sample_received',
                              'worksheetanalysis_review_state': 'unassigned'}
        self.show_editable_border = True
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url + "/add_analysis"
        self.show_sort_column = False
        self.show_select_row = True
        self.show_select_column = True
        self.show_filters = False
        self.pagesize = 50

        self.columns = {
            'ClientName': {'title': _('Client')},
            'getClientOrderNumber': {'title': _('Order')},
            'getRequestID': {'title': _('Request ID')},
            'CategoryName': {'title': _('Category')},
            'Title': {'title': _('Analysis')},
            'getDateReceived': {'title': _('Date Received')},
            'getDueDate': {'title': _('Due Date')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'transitions': ['assign'],
             'columns':['ClientName',
                        'getClientOrderNumber',
                        'getRequestID',
                        'CategoryName',
                        'Title',
                        'getDateReceived',
                        'getDueDate'],
            },
        ]

    def folderitems(self):
        pc = getToolByName(self.context, 'portal_catalog')
        self.contentsMethod = pc
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            service = obj.getService()
            client = obj.aq_parent.aq_parent
            items[x]['getClientOrderNumber'] = obj.getClientOrderNumber()
            items[x]['getDateReceived'] = \
                TimeOrDate(obj.getDateReceived())
            items[x]['getDueDate'] = \
                TimeOrDate(obj.getDueDate())
            items[x]['CategoryName'] = service.getCategory().Title()
            items[x]['ClientName'] = client.Title()
        return items

class WorksheetAddBlankView(BikaListingView):
    contentFilter = {'portal_type': 'Analysis', 'review_state':'sample_received'}
    content_add_actions = {}
    show_editable_border = True
    show_table_only = True
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    show_filters = False
    pagesize = 20

    columns = {
        'Client': {'title': _('Client')},
        'Order': {'title': _('Order')},
        'RequestID': {'title': _('Request ID')},
        'Category': {'title': _('Category')},
        'Analysis': {'title': _('Analysis')},
        'DateReceived': {'title': _('Analysis')},
        'Due': {'title': _('Analysis')},
    }
    review_states = [
        {'title': _('All'), 'id':'all',
         'columns':['Client',
                    'Order',
                    'RequestID',
                    'Category',
                    'Analysis',
                    'DateReceived',
                    'Due'],
         'buttons':[{'cssclass': 'context',
                     'title': _('Add to worksheet'),
                     'url': ''}]
        },
    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Title'] = obj.Title()
            items[x]['Owner'] = obj.getOwnerTuple()[1]
            items[x]['CreationDate'] = obj.CreationDate() and \
                 self.context.toLocalizedTime(
                     obj.CreationDate(), long_format = 0) or ''
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])

        return items

class WorksheetAddControlView(BikaListingView):
    contentFilter = {'portal_type': 'Analysis',
                     'review_state':'sample_received'}
    content_add_actions = {}
    show_editable_border = True
    show_table_only = True
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    show_filters = False
    pagesize = 20

    columns = {
        'Client': {'title': _('Client')},
        'Order': {'title': _('Order')},
        'RequestID': {'title': _('Request ID')},
        'Category': {'title': _('Category')},
        'Analysis': {'title': _('Analysis')},
        'DateReceived': {'title': _('Analysis')},
        'Due': {'title': _('Analysis')},
    }
    review_states = [
        {'title': _('All'), 'id':'all',
         'columns':['Client',
                    'Order',
                    'RequestID',
                    'Category',
                    'Analysis',
                    'DateReceived',
                    'Due'],
         'buttons':[{'cssclass': 'context',
                     'title': _('Add to worksheet'),
                     'url': ''}]
        },
    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Title'] = obj.Title()
            items[x]['Owner'] = obj.obj.getOwnerTuple()[1]
            items[x]['CreationDate'] = obj.CreationDate() and \
                 self.context.toLocalizedTime(obj.CreationDate(), long_format = 0) or ''
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])

        return items

class WorksheetAddDuplicateView(BikaListingView):
    contentFilter = {'portal_type': 'Analysis', 'review_state':'sample_received'}
    content_add_actions = {}
    show_editable_border = True
    show_table_only = True
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    show_filters = False
    pagesize = 20

    columns = {
        'Client': {'title': _('Client')},
        'Order': {'title': _('Order')},
        'RequestID': {'title': _('Request ID')},
        'Category': {'title': _('Category')},
        'Analysis': {'title': _('Analysis')},
        'DateReceived': {'title': _('Analysis')},
        'Due': {'title': _('Analysis')},
    }
    review_states = [
        {'title': _('All'), 'id':'all',
         'columns':['Client',
                    'Order',
                    'RequestID',
                    'Category',
                    'Analysis',
                    'DateReceived',
                    'Due'],
         'buttons':[{'cssclass': 'context',
                     'title': _('Add to worksheet'),
                     'url': ''}]
        },
    ]

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['Title'] = obj.Title()
            items[x]['Owner'] = obj.obj.getOwnerTuple()[1]
            items[x]['CreationDate'] = obj.CreationDate() and \
                 self.context.toLocalizedTime(obj.CreationDate(), long_format = 0) or ''
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])

        return items

class AJAXGetWorksheetTemplates():
    """ Return Worksheet Template IDs for add worksheet dropdown """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)
        pc = getToolByName(self.context, "portal_catalog")
        templates = []
        for t in pc(portal_type = "WorksheetTemplate"):
            templates.append((t.UID, t.Title))
        return json.dumps(templates)
