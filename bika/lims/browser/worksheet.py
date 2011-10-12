from AccessControl import getSecurityManager, Unauthorized
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
from bika.lims.browser.referencesamples import ReferenceSamplesView
from bika.lims.config import ManageResults
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


def getAnalysts(context):
    """ Present the LabManagers and Analysts as options for analyst
        set the first entry to blank to force selection
    """
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

class WorksheetAnalysesView(AnalysesView):
    """ This renders the table for ManageResultsView.
    """
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
                    (ar.absolute_url(), ar.Title())
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
                    items[x]['after']['Service'] = '<img title="Blank"  width="16" height="16" src="%s/++resource++bika.lims.images/blank.png"/>' % \
                        (self.context.absolute_url())
                else:
                    items[x]['after']['Service'] = '<img title="Control" width="16" height="16" src="%s/++resource++bika.lims.images/control.png"/>' % \
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

class ManageResultsView(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/worksheet_manage_results.pt")
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
    def __call__(self):
        self.Analyses = WorksheetAnalysesView(self.context, self.request)
        return self.template()
    def getAnalysts(self):
        return getAnalysts(self.context)

class AnalysesSearchResults(BikaListingView):
    ## The table used to display Analysis search results for AddAnalysesView
    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
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

class AddAnalysesView(AnalysesView):
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
        self.Analyses = AnalysesSearchResults(self.context, self.request)
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

class AddBlankView(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/worksheet_add_control.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.title = "%s: %s" % (context.Title(), _("Add Blank Reference Analysis"))
        self.description = _("Select services in the left column.  A list of " \
                            "Blank Reference Samples which specify standard " \
                            "results for the selected services will be " \
                            "displayed.  Select the reference sample to use, "
                            "and the position in which it will be inserted.")

    def __call__(self):
        self.Services = WorksheetServicesView(self.context, self.request)
        return self.template()

    def getAvailablePositions(self):
        """ Return 'b' blank positions defined by the worksheettemplate
            if the worksheet doesn't already have a blank reference there
        """
        positions = []
        layout = self.context.getLayout()
        used_positions = [slot['position'] for slot in layout \
                          if slot['container_uid']]
        wst = self.context.getWorksheetTemplate()
        if wst:
            wstlayout = wst.getLayout()
            available_positions = [slot['pos'] for slot in wstlayout \
                                   if slot['pos'] not in used_positions and \
                                      slot['type'] == 'b']
        return available_positions

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

class WorksheetServicesView(BikaListingView):
    ## This table displays a list of services from this worksheet, for the
    ## add_blank_analyses and add_control_analyses views.
    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.content_add_actions = {}
        self.contentFilter = {'portal_type': 'Analysis',
                              'review_state':'impossible_state'}
        self.show_editable_border = True
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url + "/add_blank"
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = True
        self.show_filters = False

        self.columns = {
            'Service': {'title': _('Service')},
            'Requests': {'title': _('Requests')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'transitions': [],
             'columns':['Service'], #, 'Requests'],
            },
        ]

    def folderitems(self):
        pc = getToolByName(self.context, 'portal_catalog')
        services = {} # uid:item_dict
        for analysis in self.context.getAnalyses():
            service = analysis.getService()
            service_uid = service.UID()
            ar = analysis.aq_parent
            if service_uid in services:
                services[service_uid]['Requests'].append(ar)
            else:
                services[service_uid] = {
                    'obj': service,
                    'Service': service.Title(),
                    'Requests': [ar,]
                }
        items = []
        for k,v in services.items():
            path = hasattr(v['obj'], 'getPath') and v['obj'].getPath() or \
                 "/".join(v['obj'].getPhysicalPath())
            # this folderitems doesn't subclass from the bika_listing.py
            # version, so there's lots of other stuff we have to insert here
            item = {
                'obj': v['obj'],
                'id': v['obj'].id,
                'uid': v['obj'].UID(),
                'title': v['obj'].Title(),
                'type_class': 'contenttype-AnalysisService',
                'url': v['obj'].absolute_url(),
                'relative_url': v['obj'].absolute_url(),
                'view_url': v['obj'].absolute_url(),
                'path': path,
                'Service': v['Service'],
                'Requests': '',
                'replace': {},
                'before': {},
                'after': {},
                'choices':{},
                'class': {},
                'state_class': 'state-active',
                'allow_edit': [],
            }
            for i in range(len(items)):
                items[i]['table_row_class'] = ((i + 1) % 2 == 0) and \
                     "draggable even" or "draggable odd"
            ar_hrefs = []
            for ar in v['Requests']:
                if getSecurityManager().checkPermission(ManageResults, ar):
                    url = ar.absolute_url() + "/manage_results"
                else:
                    url = ar.absolute_url()
                ar_hrefs.append("<a href='%s'>%s</a>"%(url, ar.Title()))
            item['replace']['Requests'] = ", ".join(ar_hrefs)
            items.append(item)

        return items

class ajaxGetWorksheetReferences(ReferenceSamplesView):
    """ Display reference samples matching services in this worksheet
    """
    implements(IViewView)

    def __init__(self, context, request):
        super(ajaxGetWorksheetReferences, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'ReferenceSample'}
        self.contentsMethod = self.context.portal_catalog
        self.content_add_actions = {}
        self.show_editable_border = True
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = False
        self.pagesize = 100
        # must set service_uids in __call__ before delegating to super
        self.service_uids = []
        self.columns['Services'] = {'title': _('Services')}
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns': ['ID',
                         'Title',
                         'Supplier',
                         'Definition',
                         'ExpiryDate',
                         'Services']
             },
        ]
##                         'DateSampled',
##                         'Manufacturer',
##                         'CatalogueNumber',
##                         'LotNumber',
##                         'DateReceived',
##                         'state_title']

    def folderitems(self):
        items = super(ajaxGetWorksheetReferences, self).folderitems()
        new_items = []
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            if not obj.getBlank(): continue
            ref_services = obj.getServices()
            ws_ref_services = [rs for rs in ref_services if \
                               rs.UID() in self.service_uids]
            if ws_ref_services:
                services = [rs.Title() for rs in ws_ref_services]
                items[x]['nr_services'] = len(services)
                items[x]['Services'] = \
                    ", ".join(services)
                items[x]['replace'] = {}
                new_items.append(items[x])

        new_items = sorted(new_items, key = itemgetter('nr_services'))
        new_items.reverse()

        # re-do the pretty css odd/even classes
        for i in range(len(new_items)):
            new_items[i]['table_row_class'] = ((i + 1) % 2 == 0) and \
                "draggable even" or "draggable odd"
        return new_items

    def __call__(self):
        self.service_uids = self.request.get('service_uids', '').split(",")
        return super(ajaxGetWorksheetReferences, self).contents_table()

class ajaxAddReferenceAnalyses(BrowserView):
    """ The add_control and add_blank screens use this view to add
        the requested reference analyses to the worksheet.
    """

    def __call__(self):
        rc = getToolByName(self.context, 'reference_catalog')
        plone.protect.PostOnly(self.request)
        plone.protect.CheckAuthenticator(self.request)

        position = self.request.position

        service_uids = self.request.service_uids.split(",")

        reference = rc.lookupObject(self.request.reference_uid)
        ref_type = reference.getBlank() and 'b' or 'c'

        ref_analysis_uids = []

        for service_uid in service_uids:
            ref_uid = reference.addReferenceAnalysis(service_uid, ref_type)
            ref_analysis_uids.append(ref_uid)

        self.context.setLayout(
            self.context.getLayout() + [{'position' : position,
                                        'container_uid' : reference.UID()},])
        self.context.setAnalyses(
            self.context.getAnalyses() + ref_analysis_uids)

        if ref_type == 'b':
            message = _('Blank analysis has been assigned')
        else:
            message = _('Control analysis has been assigned')
        self.context.plone_utils.addPortalMessage(message)



class ajaxSetAnalyst(BrowserView):
    """ The Analysis dropdown uses this to set the analysis immediately when
        a name is selected from the Analyst dropdown.
    """

    def __call__(self):
        rc = getToolByName(self.context, 'reference_catalog')
        mtool = getToolByName(self, 'portal_membership')
        plone.protect.PostOnly(self.request)
        plone.protect.CheckAuthenticator(self.request)
        value = request.get('value', '')
        if not value:
            return
        if not mtool.getMemberById(analyst):
            return
        self.context.setAnalyst(value)

class ajaxGetServices(BrowserView):
    """ When a Category is selected in the add_analyses search screen, this
        function returns a list of services from the selected category.
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        pc = getToolByName(self.context, 'portal_catalog')
        return json.dumps([(c.UID, c.Title) for c in \
                pc(portal_type='AnalysisService',
                   getCategoryUID=self.request.get('getCategoryUID', ''),
                   inactive_state='active')])
