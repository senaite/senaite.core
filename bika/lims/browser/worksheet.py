from DateTime import DateTime
from DocumentTemplate import sequence
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import DisplayList
from Products.Five.browser import BrowserView
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.interfaces import IWorksheet
from bika.lims.utils import TimeOrDate
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
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
        skiplist = self.request.get('workflow_skiplist', [])
        action, came_from = WorkflowAction._get_form_workflow_action(self)

        if 'Notes' in form:
            self.context.setNotes(form['Notes'])
##   ->js     if 'Analyst' in form:
##            self.context.setAnalyst(form['Analyst'])

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
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())
            self.request.response.redirect(self.destination_url)
        ## assign
        elif action == 'assign':
            selected_analyses = WorkflowAction._get_selected_items(self)
            selected_analysis_uids = selected_analyses.keys()

            if selected_analyses:
                for uid in selected_analysis_uids:
                    analysis = rc.lookupObject(uid)
                    workflow.doActionFor(analysis, 'assign')
                    self.context.addAnalysis(analysis)

            self.destination_url = self.context.absolute_url() + "/manage_results"
            self.request.response.redirect(self.destination_url)
        ## unassign
        elif action == 'unassign':
            selected_analyses = WorkflowAction._get_selected_items(self)
            selected_analysis_uids = selected_analyses.keys()

            if selected_analyses:
                for uid in selected_analysis_uids:
                    analysis = rc.lookupObject(uid)
                    workflow.doActionFor(analysis, 'unassign')
                    self.context.removeAnalysis(analysis)

            self.destination_url = self.context.absolute_url() + "/manage_results"
            self.request.response.redirect(self.destination_url)
        else:
            # default bika_listing.py/WorkflowAction for other transitions
            WorkflowAction.__call__(self)

# Present the LabManagers and Analysts as options for analyst
# set the first entry to blank to force selection
def getAnalysts(context):
    mtool = getToolByName(context, 'portal_membership')
    analysts = {}
    pairs = [(' ', ' '), ]
    analysts = mtool.searchForMembers(roles = ['LabManager', 'Analyst'])
    for member in analysts:
        uid = member.getId()
        fullname = member.getProperty('fullname')
        if fullname is None:
            continue
        pairs.append((uid, fullname))
    return pairs


class WorksheetAddView(BrowserView):
    """ This creates a new Worksheet and redirects to it.
        If a template was selected, the worksheet is pre-populated here.
    """
    implements(IViewView)

    def getAnalysts(self):
        return getAnalysts(self.context)

    def __call__(self):
        form = self.request.form
        rc = getToolByName(self.context, "reference_catalog")
        pc = getToolByName(self.context, "portal_catalog")
        wf = getToolByName(self.context, "portal_workflow")

        ws_id = self.context.generateUniqueId('Worksheet')
        self.context.invokeFactory(id = ws_id, type_name = 'Worksheet')
        ws = self.context[ws_id]

        # overwrite saved context UID for event subscribers
        self.request['context_uid'] = ws.UID()

        # if no template was specified, redirect to blank worksheet
        if not form.has_key('wstemplate') or not form['wstemplate']:
            ws.processForm()
            self.request.RESPONSE.redirect(ws.absolute_url() + "/add_analyses")
            return

        wst = rc.lookupObject(form['wstemplate'])
        wstlayout = wst.getLayout()
        services = wst.getService()
        wst_service_uids = [s.UID() for s in services]

        ws.setWorksheetTemplate(wst)

        Layout = [] # list of dict [{position:x, container_uid:x},]
        Analyses = [] # list of analysis objects

        # assign matching AR analyses
        for analysis in pc(portal_type = 'Analysis',
                           getServiceUID = wst_service_uids,
                           review_state = 'sample_received',
                           worksheetanalysis_review_state = 'unassigned',
                           cancellation_state = 'active',
                           sort_on = 'getDueDate'):
            analysis = analysis.getObject()
            service_uid = analysis.getService().UID()

            # if our parent object is already in the worksheet layout
            # we just add the analysis to Analyses
            parent_uid = analysis.aq_parent.UID()
            wslayout = ws.getLayout()
            if parent_uid in [l['container_uid'] for l in wslayout]:
                wf.doActionFor(analysis, 'assign')
                ws.setAnalyses(ws.getAnalyses() + [analysis, ])
                continue
            position = len(wslayout) + 1
            used_positions = [slot['position'] for slot in wslayout]
            available_positions = [row['pos'] for row in wstlayout \
                                   if row['pos'] not in used_positions and \
                                      row['type'] == 'a']
            if not available_positions:
                continue
            ws.setLayout(wslayout + [{'position': available_positions[0],
                                    'container_uid': parent_uid}, ])
            wf.doActionFor(analysis, 'assign')
            ws.setAnalyses(ws.getAnalyses() + [analysis, ])

        # find best maching reference samples for Blanks and Controls
        for t in ('b', 'c'):
            if t == 'b': form_key = 'blank_ref'
            else: form_key = 'control_ref'
            for row in [r for r in wstlayout if r['type'] == t]:
                reference_definition_uid = row[form_key]
                reference_definition = rc.lookupObject(reference_definition_uid)
                samples = pc(portal_type = 'ReferenceSample',
                             review_state = 'current',
                             inactive_state = 'active',
                             getReferenceDefinitionUID = reference_definition_uid)
                if not samples:
                    self.context.translate(
                        "message_no_references_found",
                        mapping = {'position':available_positions[0],
                                 'definition':reference_definition and \
                                 reference_definition.Title() or ''},
                        default = "No reference samples found for ${definition} at position ${position}.",
                        domain = "bika.lims")
                    break
                samples = [s.getObject() for s in samples]
                samples = [s for s in samples if s.getBlank == True]
                complete_reference_found = False
                references = {}
                for reference in samples:
                    reference_uid = reference.UID()
                    references[reference_uid] = {}
                    references[reference_uid]['services'] = []
                    references[reference_uid]['count'] = 0
                    specs = reference.getResultsRangeDict()
                    for service_uid in wst_service_uids:
                        if specs.has_key(service_uid):
                            references[reference_uid]['services'].append(service_uid)
                            references[reference_uid]['count'] += 1
                    if references[reference_uid]['count'] == len(wst_service_uids):
                        complete_reference_found = True
                        break
                if complete_reference_found:
                    ws.addAnalysis(reference)
                    wf.doActionFor(reference, 'assign')
                else:
                    # find the most complete reference sample instead
                    these_services = wst_service_uids
                    reference_keys = references.keys()
                    no_of_services = 0
                    reference = None
                    for key in reference_keys:
                        if references[key]['count'] > no_of_services:
                            no_of_services = references[key]['count']
                            reference = key
                    if reference:
                        ws.addAnalysis(reference)
                        wf.doActionFor(reference, 'assign')

        # fill duplicate positions
##        if count_d:
##            for row in wstlayout:
##                if row['type'] == 'd':
##                    position = int(row['pos'])
##                    duplicated_position = int(row['dup'])
##                    if duplicate_position in [l[0] for l in ws.getLayout()]:
##                        dup_analysis = ws.createDuplicateAnalyis()
##                            AR = used_ars[dup_pos]['ar'],
##                            Position = position,
##                            Service = used_ars[dup_pos]['serv'])
        ws.processForm()
        if ws.getLayout():
            self.request.RESPONSE.redirect(ws.absolute_url() + "/manage_results")
        else:
            self.context.plone_utils.addPortalMessage(_("No analyses were added to this worksheet."))
            self.request.RESPONSE.redirect(ws.absolute_url() + "/add_analyses")

class WorksheetAnalyses(AnalysesView):

    def __init__(self, context, request):
        AnalysesView.__init__(self, context, request)
        self.contentFilter = {}
        self.show_select_row = False
        self.show_sort_column = False
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
#            'Attachments': {'title': _('Attachments')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'transitions': ['submit', 'verify', 'retract', 'unassign'],
             'columns':['Pos',
                        'Client',
                        'Order',
                        'getRequestID',
                        'Category',
                        'Service',
                        'Result',
                        'Uncertainty',
#                        'Attachments',
                        'DueDate',
                        'state_title'],
             },
        ]

    def getAnalysts(self):
        return getAnalysts(self.context)

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
            # ar is either an AR, a Worksheet, or a ReferenceSample (analysis parent).
            ar = obj.aq_parent
            # client is either a Client, a ReferenceSupplier, or the worksheet folder.
            client = ar.aq_parent
            if ar.portal_type == 'AnalysisRequest':
                sample = obj.getSample()
                sample_icon = "<a href='%s'><img title='Sample: %s' src='++resource++bika.lims.images/sample.png'></a>" % \
                    (sample.absolute_url(), sample.Title())
            elif ar.portal_type == 'ReferenceSample':
                sample_icon = "<a href='%s'><img title='Reference: %s' src='++resource++bika.lims.images/referencesample.png'></a>" % \
                    (sample.absolute_url(), ar.Title())
            else:
                sample_icon = ''
            items[x]['replace']['getRequestID'] = "<a href='%s'>%s</a>%s" % \
                 (ar.absolute_url(), ar.Title(), sample_icon)

            items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % \
                 (client.absolute_url(), client.Title())
            items[x]['DueDate'] = \
                TimeOrDate(self.context, obj.getDueDate(), long_format = 0)
            items[x]['Order'] = ''
            if hasattr(ar, 'getClientOrderNumber'):
                order_nr = ar.getClientOrderNumber() or ''
                items[x]['Order'] = order_nr
            if obj.portal_type == 'DuplicateAnalysis':
                items[x]['after']['Pos'] = '<img title="Duplicate" width="16" height="16" src="%s/++resource++bika.lims.images/duplicate.png"/>' % \
                    (self.context.absolute_url())
            elif obj.portal_type == 'ReferenceAnalysis':
                if obj.ReferenceType == 'b':
                    items[x]['after']['Service'] += '<img title="Blank"  width="16" height="16" src="%s/++resource++bika.lims.images/blank.png"/>' % \
                        (self.context.absolute_url())
                else:
                    items[x]['after']['Service'] += '<img title="Control" width="16" height="16" src="%s/++resource++bika.lims.images/control.png"/>' % \
                        (self.context.absolute_url())
        # order the analyses into the worksheet.Layout parent ordering
        # and renumber their positions.
        layout = self.context.getLayout()
        items_by_parent = {}
        for item in items:
            obj = item['obj']
            parent_uid = obj.aq_parent.UID()
            item['Pos'] = [l['position'] for l in layout \
                           if l['container_uid'] == parent_uid][0]
            if parent_uid in items_by_parent:
                items_by_parent[parent_uid].append(item)
            else:
                items_by_parent[parent_uid] = [item, ]
        items = []
        for slot in layout:
            items += items_by_parent[slot['container_uid']]
        return items


class ManageResults(BrowserView):

    implements(IViewView)
    template = ViewPageTemplateFile("templates/worksheet_manage_results.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def __call__(self):
        self.Analyses = WorksheetAnalyses(self.context, self.request)
        return self.template()

    def getAnalysts(self):
        return getAnalysts(self.context)

class AnalysesTable(AnalysesView):
    ## The table used to display Analysis search results
    def __init__(self, context, request):
        AnalysesView.__init__(self, context, request)
        self.content_add_actions = {}
        self.contentFilter = {'portal_type': 'Analysis',
                              'review_state':'impossible_state'}
        self.show_editable_border = True
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url + "/add_analyses"
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.show_filters = False
        self.pagesize = 100

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
                TimeOrDate(self.context, obj.getDateReceived())
            items[x]['getDueDate'] = \
                TimeOrDate(self.context, obj.getDueDate())
            items[x]['CategoryName'] = service.getCategory().Title()
            items[x]['ClientName'] = client.Title()
        return items[:100]

class AddAnalyses(AnalysesView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/worksheet_add_analyses.pt")

    def __init__(self, context, request):
        AnalysesView.__init__(self, context, request)
        self.title = "%s: %s" % (context.Title(), _("Add Analyses"))
        self.description = _("")

    def getAnalysts(self):
        return getAnalysts(self.context)

    def __call__(self):
        form = self.request.form
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        contentFilter = {'portal_type': 'Analysis',
                         'review_state':'impossible_state',
                         'worksheetanalysis_review_state':'unassigned',
                         'cancellation_state':'active'}
        if 'submitted' in form:
            contentFilter['review_state'] = 'sample_received'
            if 'getARProfile' in form and form['getARProfile']:
                profile = rc.lookupObject(form['getARProfile'])
                service_uids = [s.UID() for s in profile.getService()]
                contentFilter['getServiceUID'] = service_uids
            else:
                for field in ['getCategoryUID', 'getServiceUID', 'getClientUID',]:
                    if field in form and 'any' not in form[field]:
                        contentFilter[field] = form[field]
        self.Analyses = AnalysesTable(self.context, self.request)
        self.Analyses.contentFilter = contentFilter
        return self.template()

    def getClients(self):
        pc = getToolByName(self.context, 'portal_catalog')
        return [(c.UID, c.Title) for c in \
                pc(portal_type='Client',
                   inactive_state='active',
                   sort_on = 'sortable_title')]

    def getCategories(self):
        pc = getToolByName(self.context, 'portal_catalog')
        return [(c.UID, c.Title) for c in \
                pc(portal_type='AnalysisCategory',
                   inactive_state='active',
                   sort_on = 'sortable_title')]

    def getARProfiles(self):
        """ Return Lab AR profiles """
        profiles = []
        pc = getToolByName(self.context, 'portal_catalog')
        return [(c.UID, c.Title) for c in \
                pc(portal_type = 'ARProfile',
                   getClientUID = self.context.bika_setup.bika_arprofiles.UID(),
                   inactive_state = 'active',
                   sort_on = 'sortable_title')]

class ajaxGetServices(BrowserView):
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        pc = getToolByName(self.context, 'portal_catalog')
        return json.dumps([(c.UID, c.Title) for c in \
                pc(portal_type='AnalysisService',
                   getCategoryUID=self.request.get('getCategoryUID', ''),
                   inactive_state='active')])

class AddBlankView(BikaListingView):
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
                 TimeOrDate(self.context, obj.CreationDate()) or ''
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])

        return items

class AddControlView(BikaListingView):
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
                 TimeOrDate(self.context, obj.CreationDate()) or ''
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])

        return items

class AddDuplicateView(BikaListingView):
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
                 TimeOrDate(self.context, obj.CreationDate()) or ''
            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                 (items[x]['url'], items[x]['Title'])

        return items

class ajaxSetAnalyst():
    """ The Analysis dropdown sets the analysis immediately on select. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        rc = getToolByName(self.context, 'reference_catalog')
        mtool = getToolByName(self, 'portal_membership')
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)
        value = request.get('value', '')
        if not value:
            return
        if not mtool.getMemberById(analyst):
            return
        self.context.setAnalyst(value)
