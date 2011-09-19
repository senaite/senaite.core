from DateTime import DateTime
from DocumentTemplate import sequence
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from Products.CMFCore.WorkflowCore import WorkflowException
from bika.lims.interfaces import IWorksheet
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.browser.analyses import AnalysesView
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
        action,came_from = WorkflowAction._get_form_workflow_action(self)

## assign
        if action == 'assign':
            analyses = WorkflowAction._get_selected_items(self)
            assigned = []
            if analyses:
                self.context.setAnalyses(self.context.getAnalyses() + analyses.values())
                layout = self.context.getLayout() # XXX layout
                for uid,analysis in analyses.items():
                    if uid not in skiplist:
                        workflow.doActionFor(analysis, 'assign')
                        assigned.append(analysis)

            if len(assigned) > 1:
                message = _('message_items_assigned',
                            default = "${count} analyses were assigned to this worksheet.",
                            mapping = {'count': len(assigned)})
            elif len(assigned) == 1:
                message = _("1 analysis was assigned to this worksheet.")
            else:
                message = _("No action taken.")
                self.context.plone_utils.addPortalMessage(message, 'info')
                return self.request.RESPONSE.redirect(originating_url)
            self.context.plone_utils.addPortalMessage(message, 'info')
            return self.request.RESPONSE.redirect(
                self.context.absolute_url() + "/manage_results")

## unassign
        elif action == 'unassign':
            analyses = WorkflowAction._get_selected_items(self)
            if analyses:
                self.context.setAnalyses([a for a in self.context.getAnalyses()
                                          if a not in analyses.values()])
                layout = self.context.getLayout() # XXX layout
                for uid,analysis in analyses.items():
                    if uid not in skiplist:
                        workflow.doActionFor(analysis, 'unassign')
## submit
        elif action == 'submit' and self.request.form.has_key("Result"):
            selected_analyses = WorkflowAction._get_selected_items(self)
            selected_analysis_uids = selected_analyses.keys()
            results = {}

            # first save results for entire form
            for uid, result in self.request.form['Result'][0].items():
                results[uid] = result
                analysis = selected_analyses[uid]
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

            if self.context.getReportDryMatter():
                self.context.setDryMatterResults()
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
        pu = getToolByName(self.context, "plone_utils")
        ws_id = self.context.generateUniqueId('Worksheet')
        self.context.invokeFactory(id = ws_id, type_name = 'Worksheet')
        ws = self.context[ws_id]
        ws.edit(Number = ws_id)
        analyses = []
        analysis_uids = []
        if form.has_key('wstemplate'):
            if form['wstemplate'] != '':
                wst = rc.lookupObject(form['wstemplate'])

                layout = wst.getLayout()
                services = wst.getService()
                service_uids = [s.UID() for s in services]

                count_a = 0
                count_b = 0
                count_c = 0
                count_d = 0
                for row in layout:
                    if row['type'] == 'a': count_a = count_a + 1
                    if row['type'] == 'b': count_b = count_b + 1
                    if row['type'] == 'c': count_c = count_c + 1
                    if row['type'] == 'd': count_d = count_d + 1

                selected = {}
                ars = []
                analysis_services = []
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
                            selected[ar.id]['uid'] = ar.UID()
                            ars.append(ar.id)
                        else:
                            continue
                    selected[ar.id]['analyses'].append(analysis.UID())
                    selected[ar.id]['services'].append(analysis.getServiceUID())

                used_ars = {}
                for row in layout:
                    position = int(row['pos'])
                    if row['type'] == 'a':
                        if ars:
                            ar = ars.pop(0)
                            used_ars[position] = {}
                            used_ars[position]['ar'] = selected[ar]['uid']
                            used_ars[position]['serv'] = selected[ar]['services']
                            for analysis in selected[ar]['analyses']:
                                analyses.append((position, analysis))
                    if row['type'] in ['b', 'c']:
                        ## select a reference sample for this slot
                        ## a) must be created from the same reference definition selected in ws template
                        ## b) takes the sample that handles all (or the most) services.
                        reference_definition_uid = row['sub']
                        references = {}
                        reference_found = False
                        for s in pc(portal_type = 'ReferenceSample',
                                    review_state = 'current',
                                    inactive_review_state = 'active',
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
                    ws.assignNumberedAnalyses(Analyses = analyses)

                if count_d:
                    for row in layout:
                        if row['type'] == 'd':
                            position = int(row['pos'])
                            dup_pos = int(row['dup'])
                            if used_ars.has_key(dup_pos):
                                ws.assignDuplicate(
                                    AR = used_ars[dup_pos]['ar'],
                                    Position = position,
                                    Service = used_ars[dup_pos]['serv'])

                ws.setMaxPositions(len(layout))

        ws.processForm()
        ws.reindexObject()

        dest = ws.absolute_url()
        self.request.RESPONSE.redirect(dest)

class WorksheetManageResultsView(AnalysesView):

    def __init__(self, context, request, allow_edit = False, **kwargs):
        super(WorksheetManageResultsView, self).__init__(context, request)
        self.contentFilter = {}
        self.show_select_row = True
        self.show_sort_column = True
        self.allow_edit = True

        self.columns = {
            'Pos': {'title': _('Pos')},
##            'Client': {'title': _('Client')},
            'Order': {'title': _('Order')},
            'RequestID': {'title': _('Reqest ID')},
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
##                        'Client',
                        'Order',
                        'RequestID',
                        'DueDate',
                        'Category',
                        'Service',
                        'Result',
                        'Attachments',
                        'state_title'],
             },
        ]

    @property
    def folderitems(self):
        self.contentsMethod = self.context.getFolderContents
        items = super(WorksheetManageResultsView, self).folderitems
        pos = 0
        for x, item in enumerate(items):
            obj = item['obj']
            pos += 1
            items[x]['Pos'] = pos
            service = obj.getService()
            items[x]['Category'] = service.getCategory().Title()
            items[x]['RequestID'] = obj.aq_parent.Title()
##            items[x]['Client'] = obj.aq_parent.aq_parent.Title()
            items[x]['DueDate'] = hasattr(obj, 'DueDate') and \
                self.context.toLocalizedTime(obj.DueDate, long_format=0) or ''
            items[x]['Order'] = hasattr(obj.aq_parent, 'getClientOrderNumber') \
                 and obj.aq_parent.getClientOrderNumber() or ''
            if obj.portal_type == 'DuplicateAnalysis':
                items[x]['after']['Pos'] = '<img width="16" height="16" src="%s/++resource++bika.lims.images/duplicate.png"/>'%\
                    (self.context.absolute_url())
            elif obj.portal_type == 'ReferenceAnalysis':
                if obj.ReferenceType == 'b':
                    items[x]['after'] += '<img width="16" height="16" src="%s/++resource++bika.lims.images/blank.png"/>'%\
                        (self.context.absolute_url())
                else:
                    items[x]['after'] += '<img width="16" height="16" src="%s/++resource++bika.lims.images/control.png"/>'%\
                        (self.context.absolute_url())

        return items

    def sort_analyses_on_requestid(self, analyses):
        ## Script (Python) "sort_analyses_on_requestid"
        ##bind container=container
        ##bind context=context
        ##bind namespace=
        ##bind script=script
        ##bind subpath=traverse_subpath
        ##parameters=analyses
        ##title=
        ##
        r = {}
        for a in analyses:
            ar_id = a.aq_parent.getRequestID()
            l = r.get(ar_id, [])
            l.append(a)
            r[ar_id] = l
        k = r.keys()
        k.sort()
        result = []
        for ar_id in k:
            result += r[ar_id]
        return result

class WorksheetAddAnalysisView(AnalysesView):
    def __init__(self, context, request):
        super(WorksheetAddAnalysisView, self).__init__(context, request)
        self.content_add_actions = {}
        self.contentFilter = {'portal_type': 'Analysis',
                              'review_state':'sample_received',
                              'worksheetanalysis_review_state': 'unassigned'}
        self.show_editable_border = True
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url  + "/add_analysis"
        self.show_sort_column = False
        self.show_select_row = True
        self.show_select_column = True
        self.show_filters = True
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

    @property
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
            items[x]['getDateReceived'] = self.context.toLocalizedTime(
                obj.getDateReceived(), long_format = 0)
            items[x]['getDueDate'] = self.context.toLocalizedTime(
                obj.getDueDate(), long_format = 0)
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
    show_filters = True
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

    @property
    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['getNumber'] = obj.getNumber()
            items[x]['getOwnerUserID'] = obj.getOwnerUserID()
            items[x]['CreationDate'] = obj.CreationDate() and \
                 self.context.toLocalizedTime(
                     obj.CreationDate(), long_format = 0) or ''
            items[x]['replace']['getNumber'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getNumber'])

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
    show_filters = True
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

    @property
    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['getNumber'] = obj.getNumber()
            items[x]['getOwnerUserID'] = obj.getOwnerUserID()
            items[x]['CreationDate'] = obj.CreationDate() and \
                 self.context.toLocalizedTime(obj.CreationDate(), long_format = 0) or ''
            items[x]['replace']['getNumber'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getNumber'])

        return items

class WorksheetAddDuplicateView(BikaListingView):
    contentFilter = {'portal_type': 'Analysis', 'review_state':'sample_received'}
    content_add_actions = {}
    show_editable_border = True
    show_table_only = True
    show_sort_column = False
    show_select_row = False
    show_select_column = True
    show_filters = True
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

    @property
    def folderitems(self):
        items = BikaListingView.folderitems(self)
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            items[x]['getNumber'] = obj.getNumber()
            items[x]['getOwnerUserID'] = obj.getOwnerUserID()
            items[x]['CreationDate'] = obj.CreationDate() and \
                 self.context.toLocalizedTime(obj.CreationDate(), long_format = 0) or ''
            items[x]['replace']['getNumber'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['getNumber'])

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
        for t in pc(portal_type="WorksheetTemplate"):
            templates.append((t.UID, t.Title))
        return json.dumps(templates)
