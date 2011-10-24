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
from bika.lims.browser.referencesample import ReferenceSamplesView
from bika.lims.config import ManageResults
from bika.lims.interfaces import IWorksheet
from bika.lims.utils import isActive, TimeOrDate
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.app.component.hooks import getSite
from zope.component import getMultiAdapter
from zope.interface import implements
from bika.lims import EditResults
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
            results = {}
            hasInterims = {}

            # first save results for entire form
            for uid, result in self.request.form['Result'][0].items():
                if uid in selected_analyses:
                    analysis = selected_analyses[uid]
                else:
                    analysis = rc.lookupObject(uid)
                if not analysis:
                    # ignore result if analysis object no longer exists
                    continue
                if not(getSecurityManager().checkPermission(EditResults, analysis)):
                    # or changes no longer allowed
                    continue
                if not isActive(analysis):
                    # or it's cancelled
                    continue
                results[uid] = result
                service = analysis.getService()
                interims = form["InterimFields"][0][uid]
                interimFields = json.loads(interims)
                if len(interimFields) > 0:
                    hasInterims[uid] = True
                else:
                    hasInterims[uid] = False
                unit = service.getUnit()
                analysis.edit(
                    Result = result,
                    InterimFields = interimFields,
                    Retested = form.has_key('retested') and \
                               form['retested'].has_key(uid),
                    Unit = unit and unit or '')

            # discover which items may be submitted
            submissable = []
            for uid, analysis in selected_analyses.items():
                if uid not in results:
                    continue
                if not results[uid]:
                    continue
                can_submit = True
                for dependency in analysis.getDependencies():
                    dep_state = workflow.getInfoFor(dependency, 'review_state')
                    if hasInterims[uid]:
                        if dep_state in ('sample_due', 'sample_received', 'attachment_due', 'to_be_verified',):
                            can_submit = False
                            break
                    else:
                        if dep_state in ('sample_due', 'sample_received',):
                            can_submit = False
                            break
                for dependency in analysis.getDependencies():
                    if workflow.getInfoFor(dependency, 'review_state') in \
                       ('sample_due', 'sample_received'):
                        can_submit = False
                if can_submit:
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
                    # Double-check the state first
                    if (workflow.getInfoFor(analysis, 'worksheetanalysis_review_state') == 'unassigned'
                    and workflow.getInfoFor(analysis, 'review_state') == 'sample_received'
                    and workflow.getInfoFor(analysis, 'cancellation_state') == 'active'):
                        self.context.addAnalysis(analysis)
                        workflow.doActionFor(analysis, 'assign')
                        # Note: subscriber might assign the AR and/or retract the worksheet

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
                        self.context._delObject(analysis.id)
                        continue
                    self.context.removeAnalysis(analysis)
                    workflow.doActionFor(analysis, 'unassign')

            self.destination_url = self.context.absolute_url() + "/manage_results"
            self.request.response.redirect(self.destination_url)
        else:
            # default bika_listing.py/WorkflowAction for other transitions
            WorkflowAction.__call__(self)


def getAnalysts(context):
    """ Present the LabManagers and Analysts as options for analyst
    """
    mtool = getToolByName(context, 'portal_membership')
    analysts = {}
    member = mtool.getAuthenticatedMember()
    pairs = []
    analysts = mtool.searchForMembers(roles = ['Manager', 'LabManager', 'Analyst'])
    for member in analysts:
        uid = member.getId()
        fullname = member.getProperty('fullname')
        if fullname is None:
            continue
        pairs.append((uid, fullname))
    return pairs

def getAnalystName(context):
    """ Returns the name of the currently assigned analyst
    """
    mtool = getToolByName(context, 'portal_membership')
    analyst = context.getAnalyst().strip()
    analyst_member = mtool.getMemberById(analyst)
    if analyst_member != None:
        return analyst_member.getProperty('fullname')
    else:
        return ''

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
            'Pos': {'title': _('Position')},
            'DueDate': {'title': _('Due date')},
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

    def getAnalystName(self):
        return getAnalystName(self.context)

    def folderitems(self):
        self.contentsMethod = self.context.getFolderContents
        items = AnalysesView.folderitems(self)
        layout = self.context.getLayout()
        highest_position = 0
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
            highest_position = max(highest_position, pos)
            items[x]['Pos'] = pos
            items[x]['colspan'] = {'Pos':1}
            service = obj.getService()
            items[x]['Category'] = service.getCategory().Title()
            items[x]['DueDate'] = \
                TimeOrDate(self.context, obj.getDueDate(), long_format = 0)
            items[x]['Order'] = ''

        # insert placeholder row items in the gaps
        empties = []
        used = [int(slot['position']) for slot in layout]
        for pos in range(1, highest_position+1):
            if pos not in used:
                empties.append(pos)
                item = {}
                item.update({
                    'allow_edit': False,
                    'obj': self.context,
                    'id': self.context.id,
                    'uid': self.context.UID(),
                    'title': self.context.Title(),
                    'type_class': 'blank-worksheet-row',
                    'url': self.context.absolute_url(),
                    'relative_url': self.context.absolute_url(),
                    'view_url': self.context.absolute_url(),
                    'path': "/".join(self.context.getPhysicalPath()),
                    'before': {},
                    'after': {},
                    'choices': {},
                    'class': {},
                    'state_class': 'state-empty',
                    'allow_edit': [],
                    'colspan': {'Pos':len(self.columns) + len(self.interim_fields)},
                    'rowspan': {'Pos':1},
                    'Pos': pos,
                    'Service': '',
                    'state_title': 's'})
                item['replace'] = {
                    'Pos': "<table width='100%' cellpadding='0' cellspacing='0'>" +\
                            "<tr><td class='pos'>%s</td>"%pos + \
                            "<td align='right'>&nbsp;</td></tr></table>",
                    'select_column': '',
                    }
                items.append(item)

        items = sorted(items, key = itemgetter('Service'))
        items = sorted(items, key = itemgetter('Pos'))

        slot_items = {} # pos:[item_nrs]
        for x in range(len(items)):
            p = items[x]['Pos']
            if p in slot_items:
                slot_items[p].append(x)
            else:
                slot_items[p] = [x, ]
        actual_table_position = -1
        # The first item in items[this position] gets a rowspan for it's
        # "Position" column, which spans all other table rows in this position.
        for pos, pos_items in slot_items.items():
            actual_table_position += 1
            x = pos_items[0]
            if pos in empties:
                continue

            # first set Pos column for this row, to have a rowspan
            items[x]['rowspan'] = {'Pos': len(pos_items)}
            for y in pos_items:
                # then set our slot's odd/even css
                for k in self.columns.keys():
                    cl = (actual_table_position % 2 == 0) and "even" or "odd"
                    items[y]['class'][k] = cl
                    items[y]['class']['select_column'] = cl
                items[y]['table_row_class'] = ""

            # fill the rowspan with a little table
            obj = items[x]['obj']
            # parent is either an AR, a Worksheet, or a
            # ReferenceSample (analysis parent).
            parent = obj.aq_parent
            if parent.aq_parent.portal_type == "WorksheetFolder":
                # we're a duplicate; get original object's client
                client = obj.getAnalysis().aq_parent.aq_parent
            elif parent.aq_parent.portal_type == "ReferenceSupplier":
                # we're a reference sample; get reference definition
                client = obj.getReferenceDefinition()
            else:
                client = parent.aq_parent
            pos_text = "<table width='100%%' cellpadding='0' cellspacing='0' style='padding-bottom:5px;'><tr>" + \
                       "<td class='pos' rowspan='3'>%s</td>" % pos
            pos_text += "<td class='pos_top'><a href='%s'>%s</a></td>" % \
                (client.absolute_url(), client.Title())
            pos_text += "<td class='pos_top_icons' rowspan='3'>"
            if obj.portal_type == 'DuplicateAnalysis':
                pos_text += "<img title='%s' src='%s/++resource++bika.lims.images/duplicate.png'/>" % (_("Duplicate"), self.context.absolute_url())
                pos_text += "<br/>"
            elif obj.portal_type == 'ReferenceAnalysis' and obj.ReferenceType == 'b':
                pos_text += "<img title='%s' width='16' height='16' src='%s/++resource++bika.lims.images/blank.png'/>" % (_("Blank"), self.context.absolute_url())
                pos_text += "<br/>"
            elif obj.portal_type == 'ReferenceAnalysis' and obj.ReferenceType == 'c':
                pos_text += "<img title='%s' width='16' height='16' src='%s/++resource++bika.lims.images/control.png'/>" % (_("Control"), self.context.absolute_url())
                pos_text += "<br/>"
            if parent.portal_type == 'AnalysisRequest':
                sample = parent.getSample()
                pos_text += "<a href='%s'><img title='%s' src='++resource++bika.lims.images/sample.png'></a>" % (sample.absolute_url(), sample.Title())
            elif parent.portal_type == 'ReferenceSample':
                pos_text += "<a href='%s'><img title='%s' src='++resource++bika.lims.images/referencesample.png'></a>" % (parent.absolute_url(), parent.Title())
            pos_text += "</td></tr>"

            pos_text += "<tr><td>"
            if parent.portal_type == 'AnalysisRequest':
                pos_text += "<a href='%s'>%s</a>" % (parent.absolute_url(), parent.Title())
            elif parent.portal_type == 'ReferenceSample':
                pos_text += "<a href='%s'>%s</a>" % (parent.absolute_url(), parent.Title())
            elif parent.portal_type == 'Worksheet':
                parent = obj.getAnalysis().aq_parent
                pos_text += "<a href='%s'>(%s)</a>" % (parent.absolute_url(), parent.Title())
            pos_text += "</td></tr>"


##            if hasattr(parent, 'getClientOrderNumber'):
##                o = parent.getClientOrderNumber()

            # sampletype
            pos_text += "<tr><td>"
            if obj.portal_type == 'Analysis':
                pos_text += obj.aq_parent.getSample().getSampleType().Title()
            elif obj.portal_type == 'ReferenceAnalysis':
                pos_text += "" #obj.aq_parent.getReferenceDefinition().Title()
            elif obj.portal_type == 'DuplicateAnalysis':
                pos_text += obj.getAnalysis().aq_parent.getSample().getSampleType().Title()
            pos_text += "</td></tr>"

            # barcode
            barcode = parent.id.replace("-","")
            if obj.portal_type == 'DuplicateAnalysis':
                barcode += "D"
            pos_text += "<tr><td class='barcode' colspan='3'><div id='barcode_%s'></div>" % barcode + \
                "<script type='text/javascript'>$('#barcode_%s').barcode('%s', 'code39', {'barHeight':15, addQuietZone:false, showHRI: false })</script>" %(barcode, barcode) + \
                "</td></tr>"

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

    def getAnalystName(self):
        return getAnalystName(self.context)

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

    def getAnalystName(self):
        return getAnalystName(self.context)

    def __call__(self):
        form = self.request.form
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        contentFilter = {'portal_type': 'Analysis',
                         'review_state':'impossible_state',
                         'worksheetanalysis_review_state':'unassigned',
                         'cancellation_state':'active'}
        if 'submitted' in form:
            contentFilter['review_state'] = 'sample_received'
            if 'getWorksheetTemplate' in form and form['getWorksheetTemplate']:
                layout = self.context.getLayout()
                wst = rc.lookupObject(form['getWorksheetTemplate'])
                self.request['context_uid'] = self.context.UID()
                self.context.applyWorksheetTemplate(wst)
                if len(self.context.getLayout()) != len(layout):
                    self.context.plone_utils.addPortalMessage(_("Workshete updated."))
                    self.request.RESPONSE.redirect(self.context.absolute_url() + "/manage_results")
                else:
                    self.context.plone_utils.addPortalMessage(_("No analyses were added to this worksheet."))
                    self.request.RESPONSE.redirect(self.context.absolute_url() + "/add_analyses")
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

    def getWorksheetTemplates(self):
        """ Return WS Templates """
        profiles = []
        pc = getToolByName(self.context, 'portal_catalog')
        return [(c.UID, c.Title) for c in \
                pc(portal_type = 'WorksheetTemplate',
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
        used_positions = [int(slot['position']) for slot in layout \
                          if slot['container_uid']]
        wst = self.context.getWorksheetTemplate()
        if wst:
            wstlayout = wst.getLayout()
            if wst.getForceWorksheetAdherence():
                available_positions = [int(slot['pos']) for slot in wstlayout \
                                       if int(slot['pos']) not in used_positions and \
                                       slot['type'] == 'b']
            else:
                available_positions = [int(slot['pos']) for slot in wstlayout \
                                       if int(slot['pos']) not in used_positions]
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
        used_positions = [int(slot['position']) for slot in layout \
                          if slot['container_uid']]
        wst = self.context.getWorksheetTemplate()
        if wst:
            wstlayout = wst.getLayout()
            if wst.getForceWorksheetAdherence():
                available_positions = [int(slot['pos']) for slot in wstlayout \
                                       if int(slot['pos']) not in used_positions and \
                                       slot['type'] == 'c']
            else:
                available_positions = [int(slot['pos']) for slot in wstlayout \
                                       if int(slot['pos']) not in used_positions]
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
        used_positions = [int(slot['position']) for slot in layout \
                          if slot['container_uid']]
        wst = self.context.getWorksheetTemplate()
        if wst:
            wstlayout = wst.getLayout()
            if wst.getForceWorksheetAdherence():
                available_positions = [int(slot['pos']) for slot in wstlayout \
                                       if int(slot['pos']) not in used_positions and \
                                       slot['type'] == 'd']
            else:
                available_positions = [int(slot['pos']) for slot in wstlayout \
                                       if int(slot['pos']) not in used_positions]
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
        for ar, pos in ars.items():
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
