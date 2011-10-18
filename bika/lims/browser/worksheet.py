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
                    if analysis.portal_type == "DuplicateAnalysis":
                        continue
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
    member = mtool.getAuthenticatedMember()
    pairs = []
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
        self.icon = "++resource++bika.lims.images/worksheet_big.png"
        self.contentFilter = {}
        self.show_select_row = False
        self.show_sort_column = False
        self.allow_edit = True

        self.columns = {
            'Pos': {'title': _('Pos')},
            'DueDate': {'title': _('Due Date')},
            'Category': {'title': _('Category')},
            'Service': {'title': _('Analysis')},
            'Result': {'title': _('Result')},
            'Uncertainty': {'title': _('+-')},
            'retested': {'title': _('Retested'), 'type':'boolean'},
##            'Attachments': {'title': _('Attachments')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'transitions': ['submit', 'verify', 'retract', 'unassign'],
             'columns':['Pos',
                        'Category',
                        'Service',
                        'Result',
                        'Uncertainty',
##                        'Attachments',
                        'DueDate',
                        'state_title'],
             },
        ]

    def getAnalysts(self):
        return getAnalysts(self.context)

    def folderitems(self):
        self.contentsMethod = self.context.getFolderContents
        items = AnalysesView.folderitems(self)
        layout = self.context.getLayout()
        for x, item in enumerate(items):
            obj = item['obj']
            if obj.portal_type in ('Analysis', 'ReferenceAnalysis'):
                pos = [slot['position'] for slot in layout if \
                       slot['container_uid'] == obj.aq_parent.UID() and \
                       slot['type'] != 'd'][0]
            elif obj.portal_type == 'DuplicateAnalysis':
                pos = [slot['position'] for slot in layout if \
                       slot['container_uid'] == obj.getAnalysis().aq_parent.UID() and \
                       slot['type'] == 'd'][0]
            pos = int(pos)
            items[x]['Pos'] = pos
            service = obj.getService()
            items[x]['Category'] = service.getCategory().Title()
            items[x]['DueDate'] = \
                TimeOrDate(self.context, obj.getDueDate(), long_format = 0)
            items[x]['Order'] = ''
        items = sorted(items, key = itemgetter('Service'))
        items = sorted(items, key = itemgetter('Pos'))

        # add rowspan tags for slot headers
        slot_items = {} # pos:[item_nrs]
        for x in range(len(items)):
            p = items[x]['Pos']
            if p in slot_items:
                slot_items[p].append(x)
            else:
                slot_items[p] = [x, ]
        csspos = -1
        for pos, pos_items in slot_items.items():
            csspos += 1
            x = pos_items[0]
            items[x]['rowspan'] = {'Pos': len(pos_items)}
            for y in pos_items:
                for k in self.columns.keys():
                    cl = (csspos % 2 == 0) and "even" or "odd"
                    items[y]['class'][k] = cl
                    items[y]['class']['select_column'] = cl
                items[y]['table_row_class'] = ""

            # ar is either an AR, a Worksheet, or a ReferenceSample (analysis parent).
            obj = items[x]['obj']
            ar = obj.aq_parent
            # client is either a Client, a ReferenceSupplier, or the worksheet folder.
            client = ar.aq_parent
            pos_text = "<table width='100%%' cellpadding='0' cellspacing='0' cellborder='0'><tr><td class='pos'>%s</td>" % pos
            pos_text += "<td class='pos_top'><a href='%s'>%s</a></td>" % (client.absolute_url(), client.Title())
            if obj.portal_type == 'DuplicateAnalysis':
                pos_text += '<td class="pos_top"><img title="Duplicate" width="16" height="16" src="%s/++resource++bika.lims.images/duplicate.png"/></td>' % (self.context.absolute_url())
            elif obj.portal_type == 'ReferenceAnalysis':
                if obj.ReferenceType == 'b':
                    pos_text += '<td class="pos_top"><img title="Blank"  width="16" height="16" src="%s/++resource++bika.lims.images/blank.png"/></td>' % (self.context.absolute_url())
                else:
                    pos_text += '<td class="pos_top"><img title="Control" width="16" height="16" src="%s/++resource++bika.lims.images/control.png"/></td>' % (self.context.absolute_url())
            else:
                pos_text += "<td></td>"
            pos_text += "</tr><tr><td></td>"
            if ar.portal_type == 'AnalysisRequest':
                sample = ar.getSample()
                sample_icon = "<a href='%s'><img title='Sample: %s' src='++resource++bika.lims.images/sample.png'></a>" % (sample.absolute_url(), sample.Title())
                pos_text += "<td><a href='%s'>%s</a></td><td>%s</td>" % (ar.absolute_url(), ar.Title(), sample_icon)
            elif ar.portal_type == 'ReferenceSample':
                sample_icon = "<a href='%s'><img title='Reference: %s' src='++resource++bika.lims.images/referencesample.png'></a>" % (ar.absolute_url(), ar.Title())
                pos_text += "<td><a href='%s'>%s</a></td><td>%s</td>" % (ar.absolute_url(), ar.Title(), sample_icon)
            elif ar.portal_type == 'Worksheet':
                ar = obj.getAnalysis().aq_parent
                pos_text += "<td><a href='%s'>(%s)</a></td><td></td>" % (ar.absolute_url(), ar.Title())
            pos_text += "</tr>"
            if hasattr(ar, 'getClientOrderNumber'):
                pos_text += "<tr><td></td><td>Order: %s</td><td></td></tr>" % (ar.getClientOrderNumber() or '')
            pos_text += "<tr><td colspan='3'><div class='barcode' value='%s'/>&nbsp;</td></tr></tr>" % (ar.id)
            pos_text += "</table>"
            items[x]['replace']['Pos'] = pos_text

        return items

class ManageResultsView(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/worksheet_manage_results.pt")
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
    def __call__(self):
        self.icon = "++resource++bika.lims.images/worksheet_big.png"
        self.Analyses = WorksheetAnalysesView(self.context, self.request)
        return self.template()
    def getAnalysts(self):
        return getAnalysts(self.context)

class AnalysesSearchResultsView(BikaListingView):
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
        self.icon = "++resource++bika.lims.images/worksheet_big.png"
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
                for field in ['getCategoryUID', 'getServiceUID', 'getClientUID', ]:
                    if field in form and 'any' not in form[field]:
                        contentFilter[field] = form[field]
        self.Analyses = AnalysesSearchResultsView(self.context, self.request)
        self.Analyses.contentFilter = contentFilter
        return self.template()

    def getClients(self):
        pc = getToolByName(self.context, 'portal_catalog')
        return [(c.UID, c.Title) for c in \
                pc(portal_type = 'Client',
                   inactive_state = 'active',
                   sort_on = 'sortable_title')]

    def getCategories(self):
        pc = getToolByName(self.context, 'portal_catalog')
        return [(c.UID, c.Title) for c in \
                pc(portal_type = 'AnalysisCategory',
                   inactive_state = 'active',
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
        self.icon = "++resource++bika.lims.images/worksheet_big.png"
        self.title = "%s: %s" % (context.Title(), _("Add Blank Reference"))
        self.description = _("Select services in the left column to locate " \
                             "reference samples. Select a reference by clicking it. ")

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
        else:
            available_positions = []
        return available_positions

class AddControlView(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/worksheet_add_control.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = "++resource++bika.lims.images/worksheet_big.png"
        self.title = "%s: %s" % (context.Title(), _("Add Control Reference"))
        self.description = _("Select services in the left column to locate " \
                             "reference samples. Select a reference by clicking it. ")
    def __call__(self):
        self.Services = WorksheetServicesView(self.context, self.request)
        return self.template()

    def getAvailablePositions(self):
        """ Return 'c' control positions defined by the worksheettemplate
            if the worksheet doesn't already have a control reference there
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
                                      slot['type'] == 'c']
        else:
            available_positions = []
        return available_positions

class AddDuplicateView(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/worksheet_add_duplicate.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = "++resource++bika.lims.images/worksheet_big.png"
        self.title = "%s: %s" % (context.Title(), _("Add Duplicates"))
        self.description = _("Select a destinaton position and the AR to duplicate.")

    def __call__(self):
        self.ARs = WorksheetARsView(self.context, self.request)
        return self.template()

    def getAvailablePositions(self):
        """ Return 'd' duplicate positions defined by the worksheettemplate
            if the worksheet layout doesn't already have data for that slot
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
                                      slot['type'] == 'd']
        else:
            available_positions = []
        return available_positions

class WorksheetARsView(BikaListingView):
    ## This table displays a list of ARs referenced by this worksheet.
    ## used in add_duplicate view.
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
        self.show_select_column = False
        self.show_filters = False

        self.columns = {
            'Position': {'title': _('Position')},
            'RequestID': {'title': _('Request ID')},
            'Client': {'title': _('Client')},
            'DateRequested': {'title': _('Date Requested')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'transitions': [],
             'columns':['Position', 'RequestID', 'Client', 'DateRequested'],
            },
        ]

    def folderitems(self):
        pc = getToolByName(self.context, 'portal_catalog')
        rc = getToolByName(self.context, 'reference_catalog')
        services = {} # uid:item_dict
        ars = {}
        for slot in self.context.getLayout():
            if slot['type'] != 'a':
                continue
            ar = slot['container_uid']
            if not ars.has_key(ar):
                ars[ar] = slot['position']
        items = []
        for ar,pos in ars.items():
            ar = rc.lookupObject(ar)
            path = "/".join(ar.getPhysicalPath())
            # this folderitems doesn't subclass from the bika_listing.py
            # so we create items from scratch
            item = {
                'obj': ar,
                'id': ar.id,
                'uid': ar.UID(),
                'title': ar.Title(),
                'type_class': 'contenttype-AnalysisService',
                'url': ar.absolute_url(),
                'relative_url': ar.absolute_url(),
                'view_url': ar.absolute_url(),
                'path': path,
                'Position': pos,
                'RequestID': ar.id,
                'Client': ar.aq_parent.Title(),
                'DateRequested': TimeOrDate(ar, ar.getDateRequested()),
                'replace': {},
                'before': {},
                'after': {},
                'choices':{},
                'class': {},
                'state_class': 'state-active',
                'allow_edit': [],
            }
            ar_hrefs = []
            items.append(item)
        items = sorted(items, key = itemgetter('Position'))
        for i in range(len(items)):
            items[i]['table_row_class'] = ((i + 1) % 2 == 0) and \
                 "draggable even" or "draggable odd"

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
                    'Requests': [ar, ]
                }
        items = []
        for k, v in services.items():
            path = hasattr(v['obj'], 'getPath') and v['obj'].getPath() or \
                 "/".join(v['obj'].getPhysicalPath())
            # if the service has dependencies, it can't have reference analyses
            calculation = v['obj'].getCalculation()
            if calculation and calculation.getDependentServices():
                continue
            # this folderitems doesn't subclass from the bika_listing.py
            # so we create items from scratch
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
            ar_hrefs = []
            for ar in v['Requests']:
                if getSecurityManager().checkPermission(ManageResults, ar):
                    url = ar.absolute_url() + "/manage_results"
                else:
                    url = ar.absolute_url()
                ar_hrefs.append("<a href='%s'>%s</a>" % (url, ar.Title()))
            item['replace']['Requests'] = ", ".join(ar_hrefs)
            items.append(item)

        for i in range(len(items)):
            items[i]['table_row_class'] = ((i + 1) % 2 == 0) and \
                 "draggable even" or "draggable odd"

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
        # must set control_type='b' or 'c' in __call__ before delegating
        self.control_type = ""
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

    def folderitems(self):
        items = super(ajaxGetWorksheetReferences, self).folderitems()
        new_items = []
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            if self.control_type == 'b' and not obj.getBlank(): continue
            if self.control_type == 'c' and obj.getBlank(): continue
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
        self.control_type = self.request.get('control_type', '')
        if not self.control_type:
            return _("No control type specified")
        return super(ajaxGetWorksheetReferences, self).contents_table()

class ajaxAddReferenceAnalyses(BrowserView):
    """ The add_control and add_blank screens use this view to add
        the requested reference analyses to the worksheet.
    """

    def __call__(self):
        rc = getToolByName(self.context, 'reference_catalog')
        plone.protect.PostOnly(self.request)
        plone.protect.CheckAuthenticator(self.request)

        # parse request
        service_uids = self.request.get('service_uids', '').split(",")
        if not service_uids:
            return
        position = self.request.get('position', '')
        if not position:
            return
        reference_uid = self.request.get('reference', '')
        reference = rc.lookupObject(reference_uid)
        if not reference:
            return
        ref_type = reference.getBlank() and 'b' or 'c'

        ref_analyses = self.context.addReferences(position,
                                                  reference,
                                                  service_uids)

        if not ref_analyses:
            message = _('No reference analyses were created')
        elif ref_type == 'b':
            message = _('Blank analysis has been assigned')
        else:
            message = _('Control analysis has been assigned')
        self.context.plone_utils.addPortalMessage(message)

class ajaxAddDuplicate(BrowserView):
    """ The add_duplicate view TRs click through to here
    """

    def __call__(self):
        rc = getToolByName(self.context, 'reference_catalog')
        plone.protect.PostOnly(self.request)
        plone.protect.CheckAuthenticator(self.request)

        ar_uid = self.request.get('ar_uid', '')
        if not ar_uid:
            return
        src_slot = [slot['position'] for slot in self.context.getLayout() if \
                    slot['container_uid'] == ar_uid and slot['type'] == 'a'][0]

        position = self.request.get('position', '')
        if not position:
            return
        self.request['context_uid'] = self.context.UID()
        dups = self.context.addDuplicateAnalyses(src_slot, position)

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
                pc(portal_type = 'AnalysisService',
                   getCategoryUID = self.request.get('getCategoryUID', ''),
                   inactive_state = 'active')])
