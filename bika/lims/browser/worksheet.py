from AccessControl import getSecurityManager
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
from bika.lims.utils import isActive, TimeOrDate
from bika.lims.exportimport import instruments
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.app.component.hooks import getSite
from zope.component import getMultiAdapter
from zope.interface import implements
from bika.lims import EditResults, EditWorksheet
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
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        skiplist = self.request.get('workflow_skiplist', [])
        action, came_from = WorkflowAction._get_form_workflow_action(self)

        # XXX combine data from multiple bika listing tables.
        item_data = {}
        if 'item_data' in form:
            if type(form['item_data']) == list:
                for i_d in form['item_data']:
                    for i, d in json.loads(i_d).items():
                        item_data[i] = d
            else:
                item_data = json.loads(form['item_data'])

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
                interimFields = item_data[uid]
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
                can_submit = True
                if hasattr(analysis, 'getDependencies'):
                    dependencies = analysis.getDependencies()
                    for dependency in dependencies:
                        dep_state = workflow.getInfoFor(dependency, 'review_state')
                        if hasInterims[uid]:
                            if dep_state in ('sample_due', 'sample_received', 'attachment_due', 'to_be_verified',):
                                can_submit = False
                                break
                        else:
                            if dep_state in ('sample_due', 'sample_received',):
                                can_submit = False
                                break
                    for dependency in dependencies:
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
            if not(getSecurityManager().checkPermission(EditWorksheet, self.context)):
                self.request.response.redirect(self.context.absolute_url())
                return

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

            self.destination_url = self.context.absolute_url()
            self.request.response.redirect(self.destination_url)
        ## unassign
        elif action == 'unassign':
            if not(getSecurityManager().checkPermission(EditWorksheet, self.context)):
                self.request.response.redirect(self.context.absolute_url())
                return

            selected_analyses = WorkflowAction._get_selected_items(self)
            selected_analysis_uids = selected_analyses.keys()

            if selected_analyses:
                for uid in selected_analysis_uids:
                    if self.context.REQUEST.has_key('workflow_skiplist'):
                        if uid in self.context.REQUEST['workflow_skiplist']:
                            continue
                    analysis = rc.lookupObject(uid)
                    self.context.removeAnalysis(analysis)

            self.destination_url = self.context.absolute_url()
            self.request.response.redirect(self.destination_url)
        ## verify
        elif action == 'verify':
            # default bika_listing.py/WorkflowAction, but then go to view screen.
            self.destination_url = self.context.absolute_url()
            WorkflowAction.__call__(self)
        else:
            # default bika_listing.py/WorkflowAction for other transitions
            WorkflowAction.__call__(self)


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
##            'Category': {'title': _('Category')},
            'Service': {'title': _('Analysis')},
            'Result': {'title': _('Result')},
            'ResultDM': {'title': _('Dry')},
            'Uncertainty': {'title': _('+-')},
            'retested': {'title': "<img src='++resource++bika.lims.images/retested.png' title='%s'/>" % _('Retested'),
                         'type':'boolean'},
            'Attachments': {'title': _('Attachments')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'transitions': ['submit', 'verify', 'retract', 'unassign'],
             'columns':['Pos',
##                        'Category',
                        'Service',
                        'Result',
                        'Uncertainty',
                        'DueDate',
                        'state_title',
                        'Attachments']
             },
        ]

    def folderitems(self):
        self.analyst = self.context.getAnalyst().strip()
        self.instrument = self.context.getInstrument()
        self.contentsMethod = self.context.getFolderContents
        items = AnalysesView.folderitems(self)
        layout = self.context.getLayout()
        highest_position = 0
        for x, item in enumerate(items):
            obj = item['obj']
            pos = [int(slot['position']) for slot in layout if \
                   slot['analysis_uid'] == obj.UID()][0]
            highest_position = max(highest_position, pos)
            items[x]['Pos'] = pos
            items[x]['colspan'] = {'Pos':1}
            service = obj.getService()
            items[x]['Category'] = service.getCategory().Title()
            if obj.portal_type == "ReferenceAnalysis":
                items[x]['DueDate'] = ''
            else:
                items[x]['DueDate'] = \
                    TimeOrDate(self.context, obj.getDueDate(), long_format = 0)
            items[x]['Order'] = ''

        # insert placeholder row items in the gaps
        empties = []
        used = [int(slot['position']) for slot in layout]
        for pos in range(1, highest_position + 1):
            if pos not in used:
                empties.append(pos)
                item = {}
                item.update({
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
                    'Attachments': '',
                    'state_title': 's'})
                item['replace'] = {
                    'Pos': "<table width='100%' cellpadding='0' cellspacing='0'>" + \
                            "<tr><td class='pos'>%s</td>" % pos + \
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
                    if k in items[y]['class']:
                        items[y]['class'][k] += " %s" % cl
                    else:
                        items[y]['class'][k] = cl
                    items[y]['class']['select_column'] = cl
                items[y]['table_row_class'] = cl

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
            pos_text = "<table class='worksheet-position' width='100%%' cellpadding='0' cellspacing='0' style='padding-bottom:5px;'><tr>" + \
                       "<td class='pos' rowspan='3'>%s</td>" % pos
            pos_text += "<td class='pos_top'><a href='%s'>%s</a></td>" % \
                (client.absolute_url(), client.Title())
            pos_text += "<td class='pos_top_icons' rowspan='3'>"
            if obj.portal_type == 'DuplicateAnalysis':
                pos_text += "<img title='%s' src='%s/++resource++bika.lims.images/duplicate.png'/>" % (_("Duplicate"), self.context.absolute_url())
                pos_text += "<br/>"
            elif obj.portal_type == 'ReferenceAnalysis' and obj.ReferenceType == 'b':
                pos_text += "<a href='%s'><img title='%s' src='++resource++bika.lims.images/blank.png'></a>" % (parent.absolute_url(), parent.Title())
                pos_text += "<br/>"
            elif obj.portal_type == 'ReferenceAnalysis' and obj.ReferenceType == 'c':
                pos_text += "<a href='%s'><img title='%s' src='++resource++bika.lims.images/control.png'></a>" % (parent.absolute_url(), parent.Title())
                pos_text += "<br/>"
            if parent.portal_type == 'AnalysisRequest':
                sample = parent.getSample()
                pos_text += "<a href='%s'><img title='%s' src='++resource++bika.lims.images/sample.png'></a>" % (sample.absolute_url(), sample.Title())
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

            # sampletype
            pos_text += "<tr><td>"
            if obj.portal_type == 'Analysis':
                pos_text += obj.aq_parent.getSample().getSampleType().Title()
            elif obj.portal_type == 'ReferenceAnalysis':
                pos_text += "" #obj.aq_parent.getReferenceDefinition().Title()
            elif obj.portal_type == 'DuplicateAnalysis':
                pos_text += obj.getAnalysis().aq_parent.getSample().getSampleType().Title()
            pos_text += "</td></tr>"

##            # barcode
##            barcode = parent.id.replace("-", "")
##            if obj.portal_type == 'DuplicateAnalysis':
##                barcode += "D"
##            pos_text += "<tr><td class='barcode' colspan='3'><div id='barcode_%s'></div>" % barcode + \
##                "<script type='text/javascript'>$('#barcode_%s').barcode('%s', 'code39', {'barHeight':15, addQuietZone:false, showHRI: false })</script>" % (barcode, barcode) + \
##                "</td></tr>"

            pos_text += "</table>"

            items[x]['replace']['Pos'] = pos_text

        return items

class ManageResultsView(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/worksheet_manage_results.pt")
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def __call__(self):
        # Worksheet Attachmemts
        # the expandable form is handled here.
        if "AttachmentFile_file" in self.request:
            this_file =  self.request['AttachmentFile_file']
            if 'analysis_uid' in self.request:
                analysis_uid = self.request['analysis_uid']
            else:
                analysis_uid = None
            if 'Service' in self.request:
                service_uid = self.request['Service']
            else:
                service_uid = None

            tool = getToolByName(self.context, REFERENCE_CATALOG)
            if analysis_uid:
                analysis = tool.lookupObject(analysis_uid)
                attachmentid = self.context.generateUniqueId('Attachment')
                # client refers to Client in case of Analysis, and to
                #     parent Worksheet in case of DuplicateAnalysis
                if analysis.aq_parent.portal_type == 'AnalysisRequest':
                    client = analysis.aq_parent.aq_parent
                else:
                    client = analysis.aq_parent
                client.invokeFactory("Attachment",
                                     id = attachmentid)
                attachment = client._getOb(attachmentid)
                attachment.edit(
                    AttachmentFile = this_file,
                    AttachmentType = self.request['AttachmentType'],
                    AttachmentKeys = self.request['AttachmentKeys'])
                attachment.reindexObject()

                others = analysis.getAttachment()
                attachments = []
                for other in others:
                    attachments.append(other.UID())
                attachments.append(attachment.UID())
                analysis.setAttachment(attachments)

            if service_uid:
                wf_tool = getToolByName(self.context, 'portal_workflow')
                for analysis in self.context.getAnalyses():
                    if analysis.portal_type not in ('Analysis', 'DuplicateAnalysis'):
                        continue
                    if not analysis.getServiceUID() == service_uid:
                        continue
                    review_state = wf_tool.getInfoFor(analysis, 'review_state', '')
                    if not review_state in ['assigned', 'sample_received', 'to_be_verified']:
                        continue
                    attachmentid = self.context.generateUniqueId('Attachment')
                    # client refers to Client in case of Analysis, and to
                    #     parent Worksheet in case of DuplicateAnalysis
                    if analysis.aq_parent.portal_type == 'AnalysisRequest':
                        client = analysis.aq_parent.aq_parent
                    else:
                        client = analysis.aq_parent
                    client.invokeFactory("Attachment", id = attachmentid)
                    attachment = client._getOb(attachmentid)
                    attachment.edit(
                        AttachmentFile = this_file,
                        AttachmentType = self.request['AttachmentType'],
                        AttachmentKeys = self.request['AttachmentKeys'])
                    attachment.reindexObject()

                    others = analysis.getAttachment()
                    attachments = []
                    for other in others:
                        attachments.append(other.UID())
                    attachments.append(attachment.UID())
                    analysis.setAttachment(attachments)

        self.icon = "++resource++bika.lims.images/worksheet_big.png"
        self.Analyses = WorksheetAnalysesView(self.context, self.request)
        self.analystname = getAnalystName(self.context)
        self.instrumenttitle = self.context.getInstrument() and self.context.getInstrument().Title() or ''

        return self.template()

class AddAnalysesView(BikaListingView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/worksheet_add_analyses.pt")

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.icon = "++resource++bika.lims.images/worksheet_big.png"
        self.title = "%s: %s" % (context.Title(), _("Add Analyses"))
        self.description = _(" ")

        self.context_actions = {}
        # initial review state for first form display of the worksheet
        # add_analyses search view - first batch of analyses, latest first.
        self.contentFilter = {'portal_type': 'Analysis',
                              'review_state':'sample_received',
                              'worksheetanalysis_review_state':'unassigned',
                              'cancellation_state':'active'}
        self.base_url = self.context.absolute_url()
        self.view_url = self.base_url + "/add_analyses"
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        # the tal disables batching controls if pagesize=1000
        self.pagesize = 1000

        self.columns = {
            'ClientTitle': {'title': _('Client'),
                            'sortable':False},
#                            'index':'getClientTitle'},
            'getClientOrderNumber': {'title': _('Order'),
                            'sortable':False},
#                            'index':'getClientOrderNumber'},
            'getRequestID': {'title': _('Request ID'),
                            'sortable':False},
#                            'index':'getRequestID'},
            'CategoryTitle': {'title': _('Category'),
                            'sortable':False},
#                            'index':'getCategoryTitle'},
            'Title': {'title': _('Analysis'),
                            'sortable':False},
#                            'index':'sortable_title'},
            'getDateReceived': {'title': _('Date Received'),
                            'sortable':False},
#                            'index':'getDateReceived'},
            'getDueDate': {'title': _('Due Date'),
                            'sortable':False},
#                            'index':'getDueDate'},
        }
        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'transitions': ['assign'],
             'columns':['ClientTitle',
                        'getClientOrderNumber',
                        'getRequestID',
                        'CategoryTitle',
                        'Title',
                        'getDateReceived',
                        'getDueDate'],
            },
        ]

    def __call__(self):
        if not(getSecurityManager().checkPermission(EditWorksheet, self.context)):
            self.request.response.redirect(self.context.absolute_url())
            return

        form = self.request.form
        rc = getToolByName(self.context, REFERENCE_CATALOG)

        if 'submitted' in form:
            if 'getWorksheetTemplate' in form and form['getWorksheetTemplate']:
                layout = self.context.getLayout()
                wst = rc.lookupObject(form['getWorksheetTemplate'])
                self.request['context_uid'] = self.context.UID()
                self.context.applyWorksheetTemplate(wst)
                if len(self.context.getLayout()) != len(layout):
                    self.context.plone_utils.addPortalMessage(_("Worksheet updated."))
                    self.request.RESPONSE.redirect(self.context.absolute_url() + "/manage_results")
                else:
                    self.context.plone_utils.addPortalMessage(_("No analyses were added to this worksheet."))
                    self.request.RESPONSE.redirect(self.context.absolute_url() + "/add_analyses")
        for field in ['getCategoryUID', 'getServiceUID', 'getClientUID', ]:
            request_key = "%s_%s" % (self.form_id, field)
            if request_key in self.request and \
               self.request[request_key] != 'any':
                self.contentFilter[field] = self.request[request_key]
        return self.template()

    def folderitems(self):
        pc = getToolByName(self.context, 'portal_catalog')
        self.contentsMethod = pc
        items = BikaListingView.folderitems(self)
        # we really only care about the first hundred items and nothing else.
        new_items = []
        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            service = obj.getService()
            client = obj.aq_parent.aq_parent
            items[x]['getClientOrderNumber'] = obj.getClientOrderNumber()
            items[x]['getDateReceived'] = \
                TimeOrDate(self.context, obj.getDateReceived())
            DueDate = obj.getDueDate()
            items[x]['getDueDate'] = \
                TimeOrDate(self.context, DueDate)
            if DueDate < DateTime():
                items[x]['after']['DueDate'] = '<img width="16" height="16" src="%s/++resource++bika.lims.images/late.png" title="%s"/>' % \
                    (self.context.absolute_url(), _("Late analysis"))
            items[x]['CategoryTitle'] = service.getCategory().Title()
            items[x]['ClientTitle'] = client.Title()
            new_items.append(items[x])
        new_items = sorted(new_items, key = itemgetter('Title'))
        new_items = sorted(new_items, key = itemgetter('getRequestID'))
        return new_items[:100]

    def getServices(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        return [(c.UID, c.Title) for c in \
                bsc(portal_type = 'AnalysisService',
                   getCategoryUID = self.request.get('list_getCategoryUID', ''),
                   inactive_state = 'active',
                   sort_on = 'sortable_title')]

    def getClients(self):
        pc = getToolByName(self.context, 'portal_catalog')
        return [(c.UID, c.Title) for c in \
                pc(portal_type = 'Client',
                   inactive_state = 'active',
                   sort_on = 'sortable_title')]

    def getCategories(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        return [(c.UID, c.Title) for c in \
                bsc(portal_type = 'AnalysisCategory',
                   inactive_state = 'active',
                   sort_on = 'sortable_title')]

    def getWorksheetTemplates(self):
        """ Return WS Templates """
        profiles = []
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        return [(c.UID, c.Title) for c in \
                bsc(portal_type = 'WorksheetTemplate',
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
        if not(getSecurityManager().checkPermission(EditWorksheet, self.context)):
            self.request.response.redirect(self.context.absolute_url())
            return

        form = self.request.form
        if 'submitted' in form:
            rc = getToolByName(self.context, REFERENCE_CATALOG)
            # parse request
            service_uids = form['selected_service_uids'].split(",")
            position = form['position']
            reference_uid = form['reference_uid']
            reference = rc.lookupObject(reference_uid)
            self.request['context_uid'] = self.context.UID()
            ref_analyses = self.context.addReferences(position,
                                                      reference,
                                                      service_uids)
            self.request.response.redirect(
                self.context.absolute_url() + "/manage_results")
            return

        self.Services = WorksheetServicesView(self.context, self.request)
        self.Services.view_url = self.Services.base_url + "/add_blank"
        return self.template()

    def getAvailablePositions(self):
        """ Return a list of empty slot numbers
        """
        layout = self.context.getLayout()
        used_positions = [int(slot['position']) for slot in layout]
        if used_positions:
            available_positions = [pos for pos in range(1, max(used_positions) + 1) if \
                                   pos not in used_positions]
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
        if not(getSecurityManager().checkPermission(EditWorksheet, self.context)):
            self.request.response.redirect(self.context.absolute_url())
            return

        form = self.request.form
        if 'submitted' in form:
            rc = getToolByName(self.context, REFERENCE_CATALOG)
            # parse request
            service_uids = form['selected_service_uids'].split(",")
            position = form['position']
            reference_uid = form['reference_uid']
            reference = rc.lookupObject(reference_uid)
            self.request['context_uid'] = self.context.UID()
            ref_analyses = self.context.addReferences(position,
                                                      reference,
                                                      service_uids)
            self.request.response.redirect(
                self.context.absolute_url() + "/manage_results")
            return

        self.Services = WorksheetServicesView(self.context, self.request)
        self.Services.view_url = self.Services.base_url + "/add_control"
        return self.template()

    def getAvailablePositions(self):
        """ Return a list of empty slot numbers
        """
        layout = self.context.getLayout()
        used_positions = [int(slot['position']) for slot in layout]
        if used_positions:
            available_positions = [pos for pos in range(1, max(used_positions) + 1) if \
                                   pos not in used_positions]
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
        if not(getSecurityManager().checkPermission(EditWorksheet, self.context)):
            self.request.response.redirect(self.context.absolute_url())
            return

        form = self.request.form
        if 'submitted' in form:
            ar_uid = self.request.get('ar_uid', '')
            src_slot = [slot['position'] for slot in self.context.getLayout() if \
                        slot['container_uid'] == ar_uid and slot['type'] == 'a'][0]
            position = self.request.get('position', '')
            self.request['context_uid'] = self.context.UID()
            self.context.addDuplicateAnalyses(src_slot, position)
            self.request.response.redirect(
                self.context.absolute_url() + "/manage_results")
            return

        self.ARs = WorksheetARsView(self.context, self.request)
        return self.template()

    def getAvailablePositions(self):
        """ Return a list of empty slot numbers
        """
        layout = self.context.getLayout()
        used_positions = [int(slot['position']) for slot in layout]
        if used_positions:
            available_positions = [pos for pos in range(1, max(used_positions) + 1) if \
                                   pos not in used_positions]
        else:
            available_positions = []
        return available_positions


class WorksheetARsView(BikaListingView):
    ## This table displays a list of ARs referenced by this worksheet.
    ## used in add_duplicate view.
    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.context_actions = {}
        self.contentFilter = {'portal_type': 'Analysis',
                              'review_state':'impossible_state'}
        self.base_url = self.context.absolute_url()
        self.view_url = self.context.absolute_url() + "/add_duplicate"
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = False

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
        rc = getToolByName(self.context, REFERENCE_CATALOG)
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
            items.append(item)
        items = sorted(items, key = itemgetter('Position'))
        for i in range(len(items)):
            items[i]['table_row_class'] = ((i + 1) % 2 == 0) and \
                 "even" or "odd"

        return items

class WorksheetServicesView(BikaListingView):
    """ This table displays a list of services for the adding controls / blanks.
        Services which have analyses in this worksheet are selected, and their
        categories are expanded by default
    """
    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.context_actions = {}
        self.contentFilter = {'review_state':'impossible_state'}
        self.base_url = self.context.absolute_url()
        self.view_url = self.context.absolute_url()
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = True
        self.pagesize = 1000
        self.show_workflow_action_buttons = False

        self.columns = {
            'Service': {'title': _('Service'),
                        'sortable': False},
        }
        self.review_states = [
            {'id':'all',
             'title': _('All'),
             'transitions': [],
             'columns':['Service'],
            },
        ]

    def folderitems(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        ws_services = []
        for analysis in self.context.getAnalyses():
            service_uid = analysis.getService().UID()
            if service_uid not in ws_services:
                ws_services.append(service_uid)
        self.categories = []
        services = bsc(portal_type = "AnalysisService",
                       inactive_state = "active")
        items = []
        for service in services:
            # if the service has dependencies, it can't have reference analyses
            calculation = service.getObject().getCalculation()
            if calculation and calculation.getDependentServices():
                continue
            cat = service.getCategoryTitle
            if cat not in self.categories:
                self.categories.append(cat)
            # this folderitems doesn't subclass from the bika_listing.py
            # so we create items from scratch
            item = {
                'obj': service,
                'id': service.id,
                'uid': service.UID,
                'title': service.Title,
                'category': cat,
                'selected': service.UID in ws_services,
                'type_class': 'contenttype-AnalysisService',
                'url': service.absolute_url(),
                'relative_url': service.absolute_url(),
                'view_url': service.absolute_url(),
                'Service': service.Title,
                'replace': {},
                'before': {},
                'after': {},
                'choices':{},
                'class': {},
                'state_class': 'state-active',
                'allow_edit': [],
            }
            items.append(item)

        items = sorted(items, key = itemgetter('Service'))
        self.categories.sort()
        for i in range(len(items)):
            items[i]['table_row_class'] = ((i + 1) % 2 == 0) and \
                 "even" or "odd"

        return items

class ajaxGetWorksheetReferences(ReferenceSamplesView):
    """ Display reference samples matching services in this worksheet
    """
    implements(IViewView)

    def __init__(self, context, request):
        super(ajaxGetWorksheetReferences, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'ReferenceSample'}
        self.contentsMethod = self.context.portal_catalog
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = False
        self.show_workflow_action_buttons = False
        self.pagesize = 100
        # must set service_uids in __call__ before delegating to super
        self.service_uids = []
        # must set control_type='b' or 'c' in __call__ before delegating
        self.control_type = ""
        self.columns['Services'] = {'title': _('Services')}
        self.columns['Definition'] = {'title': _('Reference Definition')}
        self.review_states = [
            {'title': _('All'), 'id':'all',
             'columns': ['ID',
                         'Title',
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
                items[x]['Definition'] = obj.getReferenceDefinition().Title()
                items[x]['Services'] = \
                    ", ".join(services)
                items[x]['replace'] = {}
                new_items.append(items[x])

        new_items = sorted(new_items, key = itemgetter('nr_services'))
        new_items.reverse()

        # re-do the pretty css odd/even classes
        for i in range(len(new_items)):
            new_items[i]['table_row_class'] = ((i + 1) % 2 == 0) and \
                "even" or "odd"

        return new_items

    def __call__(self):
        self.service_uids = self.request.get('service_uids', '').split(",")
        self.control_type = self.request.get('control_type', '')
        if not self.control_type:
            return _("No control type specified")
        return super(ajaxGetWorksheetReferences, self).contents_table()

class ExportView(BrowserView):
    """
    """
    def __call__(self):

        instrument = self.context.getInstrument()
        if not instrument:
            message = _("You must select an instrument before you can export this worksheet.")
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        exim = instrument.getDataInterface()
        if not exim:
            message = _("This instrument has no Data Interface selected.")
            self.context.plone_utils.addPortalMessage(message, 'info')
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        # exim refers to filename in instruments/
        if type(exim) == list:
            exim = exim[0]
        exim = exim.lower()

        # search instruments module for 'exim' module
        if not hasattr(instruments, exim):
            message = _("Instrument exporter not found.")
            self.context.plone_utils.addPortalMessage(message, 'error')
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        exim = getattr(instruments, exim)
        exporter = exim.Export(self.context, self.request)
        data = exporter(self.context.getAnalyses())
        pass

class ajaxGetServices(BrowserView):
    """ When a Category is selected in the add_analyses search screen, this
        function returns a list of services from the selected category.
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        return json.dumps([(c.UID, c.Title) for c in \
                bsc(portal_type = 'AnalysisService',
                   getCategoryUID = self.request.get('getCategoryUID', ''),
                   inactive_state = 'active',
                   sort_on = 'sortable_title')])

class ajaxAttachAnalyses(BrowserView):
    """ In attachment add form,
        the analyses dropdown combo uses this as source.
        Form is handled by the worksheet ManageResults code
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = self.request['searchTerm'].lower()
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        attachable_states = ('assigned', 'sample_received', 'to_be_verified')
        wf = getToolByName(self.context, 'portal_workflow')
        analysis_to_slot = {}
        for s in self.context.getLayout():
            analysis_to_slot[s['analysis_uid']] = int(s['position'])
        analyses = list(self.context.getAnalyses(full_objects = True))
        # Duplicates belong to the worksheet, so we must add them individually
        for i in self.context.objectValues():
            if i.portal_type == 'DuplicateAnalysis':
                analyses.append(i)
        rows = []
        for analysis in analyses:
            review_state = wf.getInfoFor(analysis, 'review_state', '')
            if analysis.portal_type in ('Analysis', 'DuplicateAnalysis'):
                if review_state not in attachable_states:
                    continue
                parent = analysis.getRequestID()
                service = analysis.getService()
            elif analysis.portal_type == 'ReferenceAnalysis':
                if review_state not in attachable_states:
                    continue
                parent = analysis.aq_parent.Title()
                service = analysis.getService()
            rows.append({'analysis_uid': analysis.UID(),
                         'slot': analysis_to_slot[analysis.UID()],
                         'service': service and service.Title() or '',
                         'parent': parent,
                         'type': analysis.portal_type})

        # if there's a searchTerm supplied, restrict rows to those
        # who contain at least one field that starts with the chars from
        # searchTerm.
        if searchTerm:
            orig_rows = rows
            rows = []
            for row in orig_rows:
                matches = [v for v in row.values() \
                           if str(v).lower().startswith(searchTerm)]
                if matches:
                    rows.append(row)

        rows = sorted(rows, key = itemgetter(sidx and sidx or 'slot'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        ret = {'page':page,
               'total':pages,
               'records':len(rows),
               'rows':rows[ (int(page)-1)*int(nr_rows) : int(page)*int(nr_rows) ]}

        return json.dumps(ret)
