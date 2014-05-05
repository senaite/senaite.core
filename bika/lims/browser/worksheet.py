# coding=utf-8
from AccessControl import getSecurityManager
from Products.CMFPlone.utils import _createObjectByType
from bika.lims import bikaMessageFactory as _
from bika.lims import EditResults, EditWorksheet, ManageWorksheets
from bika.lims import PMF, logger
from bika.lims.browser import BrowserView
from bika.lims.browser.analyses import AnalysesView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.browser.referencesample import ReferenceSamplesView
from bika.lims.exportimport import instruments
from bika.lims.interfaces import IFieldIcons
from bika.lims.interfaces import IWorksheet
from bika.lims.subscribers import doActionFor
from bika.lims.subscribers import skip
from bika.lims.utils import to_utf8, getHiddenAttributesForClass
from bika.lims.utils import getUsers, isActive, tmpID
from DateTime import DateTime
from DocumentTemplate import sequence
from operator import itemgetter
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.interface import implements
from bika.lims.browser.referenceanalysis import AnalysesRetractedListReport
from DateTime import DateTime
from Products.CMFPlone.i18nl10n import ulocalized_time

import plone
import plone.protect
import json


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
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        bac = getToolByName(self.context, 'bika_analysis_catalog')
        action, came_from = WorkflowAction._get_form_workflow_action(self)


        if action == 'submit':

            # Submit the form. Saves the results, methods, etc.
            self.submit()

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

            for analysis_uid in selected_analysis_uids:
                try:
                    analysis = bac(UID=analysis_uid)[0].getObject()
                except IndexError:
                    # Duplicate analyses are removed when their analyses
                    # get removed, so indexerror is expected.
                    continue
                if skip(analysis, action, peek=True):
                    continue
                self.context.removeAnalysis(analysis)

            message = PMF("Changes saved.")
            self.context.plone_utils.addPortalMessage(message, 'info')
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

    def submit(self):
        """ Saves the form
        """

        form = self.request.form
        remarks = form.get('Remarks', [{}])[0]
        results = form.get('Result',[{}])[0]
        retested = form.get('retested', {})
        methods = form.get('Method', [{}])[0]
        instruments = form.get('Instrument', [{}])[0]
        analysts = self.request.form.get('Analyst', [{}])[0]
        selected = WorkflowAction._get_selected_items(self)
        workflow = getToolByName(self.context, 'portal_workflow')
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        sm = getSecurityManager()

        hasInterims = {}

        # XXX combine data from multiple bika listing tables.
        item_data = {}
        if 'item_data' in form:
            if type(form['item_data']) == list:
                for i_d in form['item_data']:
                    for i, d in json.loads(i_d).items():
                        item_data[i] = d
            else:
                item_data = json.loads(form['item_data'])

        # Iterate for each selected analysis and save its data as needed
        for uid, analysis in selected.items():

            allow_edit = sm.checkPermission(EditResults, analysis)
            analysis_active = isActive(analysis)

            # Need to save remarks?
            if uid in remarks and allow_edit and analysis_active:
                analysis.setRemarks(remarks[uid])

            # Retested?
            if uid in retested and allow_edit and analysis_active:
                analysis.setRetested(retested[uid])

            # Need to save the instrument?
            if uid in instruments and analysis_active:
                # TODO: Add SetAnalysisInstrument permission
                # allow_setinstrument = sm.checkPermission(SetAnalysisInstrument)
                allow_setinstrument = True
                # ---8<-----
                if allow_setinstrument == True:
                    # The current analysis allows the instrument regards
                    # to its analysis service and method?
                    if (instruments[uid]==''):
                        previnstr = analysis.getInstrument()
                        if previnstr:
                            previnstr.removeAnalysis(analysis)
                        analysis.setInstrument(None);
                    elif analysis.isInstrumentAllowed(instruments[uid]):
                        previnstr = analysis.getInstrument()
                        if previnstr:
                            previnstr.removeAnalysis(analysis)
                        analysis.setInstrument(instruments[uid])
                        instrument = analysis.getInstrument()
                        instrument.addAnalysis(analysis)

            # Need to save the method?
            if uid in methods and analysis_active:
                # TODO: Add SetAnalysisMethod permission
                # allow_setmethod = sm.checkPermission(SetAnalysisMethod)
                allow_setmethod = True
                # ---8<-----
                if allow_setmethod == True and analysis.isMethodAllowed(methods[uid]):
                    analysis.setMethod(methods[uid])

            # Need to save the analyst?
            if uid in analysts and analysis_active:
                analysis.setAnalyst(analysts[uid]);

            # Need to save results?
            if uid in results and results[uid] and allow_edit \
                and analysis_active:
                interims = item_data.get(uid, [])
                analysis.setInterimFields(interims)
                analysis.setResult(results[uid])
                analysis.reindexObject()

                can_submit = True
                deps = analysis.getDependencies() \
                        if hasattr(analysis, 'getDependencies') else []
                for dependency in deps:
                    if workflow.getInfoFor(dependency, 'review_state') in \
                       ('to_be_sampled', 'to_be_preserved',
                        'sample_due', 'sample_received'):
                        can_submit = False
                        break
                if can_submit:
                    # doActionFor transitions the analysis to verif pending,
                    # so must only be done when results are submitted.
                    doActionFor(analysis, 'submit')

        # Maybe some analyses need to be retracted due to a QC failure
        # Done here because don't know if the last selected analysis is
        # a valid QC for the instrument used in previous analyses.
        # If we add this logic in subscribers.analyses, there's the
        # possibility to retract analyses before the QC being reached.
        self.retractInvalidAnalyses()

        message = PMF("Changes saved.")
        self.context.plone_utils.addPortalMessage(message, 'info')
        self.destination_url = self.request.get_header("referer",
                               self.context.absolute_url())
        self.request.response.redirect(self.destination_url)

    def retractInvalidAnalyses(self):
        """ Retract the analyses with validation pending status for which
            the instrument used failed a QC Test.
        """
        toretract = {}
        instruments = {}
        refs = []
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        selected = WorkflowAction._get_selected_items(self)
        for uid in selected.iterkeys():
            # We need to do this instead of using the dict values
            # directly because all these analyses have been saved before
            # and don't know if they already had an instrument assigned
            an = rc.lookupObject(uid)
            if an.portal_type == 'ReferenceAnalysis':
                refs.append(an)
                instrument = an.getInstrument()
                if instrument and instrument.UID() not in instruments:
                    instruments[instrument.UID()] = instrument

        for instr in instruments.itervalues():
            analyses = instr.getAnalysesToRetract()
            for a in analyses:
                if a.UID() not in toretract:
                    toretract[a.UID] = a

        retracted = []
        for analysis in toretract.itervalues():
            try:
                # add a remark to this analysis
                failedtxt = ulocalized_time(DateTime(), long_format=0)
                failedtxt = '%s: %s' % (failedtxt, _("Instrument failed reference test"))
                analysis.setRemarks(failedtxt)

                # retract the analysis
                doActionFor(analysis, 'retract')
                retracted.append(analysis)
            except:
                # Already retracted as a dependant from a previous one?
                pass

        if len(retracted) > 0:
            # Create the Retracted Analyses List
            rep = AnalysesRetractedListReport(self.context,
                                               self.request,
                                               self.portal_url,
                                               'Retracted analyses',
                                               retracted)

            # Attach the pdf to the ReferenceAnalysis (accessible
            # from Instrument's Internal Calibration Tests list
            pdf = rep.toPdf()
            for ref in refs:
                ref.setRetractedAnalysesPdfReport(pdf)

            # Send the email
            try:
                rep.sendEmail()
            except:
                pass

            # TODO: mostra una finestra amb els resultats publicats d'AS
            # que han utilitzat l'instrument des de la seva última
            # calibració vàlida, amb els emails, telèfons dels
            # contactes associats per a una intervenció manual
            pass

class ResultOutOfRange(object):
    """Return alerts for any analyses inside the context worksheet
    """
    implements(IFieldIcons)
    adapts(IWorksheet)

    def __init__(self, context):
        self.context = context

    def __call__(self, result=None, **kwargs):
        workflow = getToolByName(self.context, 'portal_workflow')
        items = self.context.getAnalyses()
        field_icons = {}
        for obj in items:
            obj = obj.getObject() if hasattr(obj, 'getObject') else obj
            uid = obj.UID()
            astate = workflow.getInfoFor(obj, 'review_state')
            if astate == 'retracted':
                continue
            adapters = getAdapters((obj, ), IFieldIcons)
            for name, adapter in adapters:
                alerts = adapter()
                if alerts:
                    if uid in field_icons:
                        field_icons[uid].extend(alerts[uid])
                    else:
                        field_icons[uid] = alerts[uid]
        return field_icons


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
        self.catalog = 'bika_analysis_catalog'
        self.contentFilter = {'portal_type':'Analysis',
                              'review_state':'sample_received',
                              'worksheetanalysis_review_state':'unassigned'}
        self.icon = self.portal_url + "/++resource++bika.lims.images/worksheet_big.png"
        self.contentFilter = {}
        self.show_select_row = False
        self.show_sort_column = False
        self.allow_edit = True
        self.show_categories = False
        self.expand_all_categories = False

        self.columns = {
            'Pos': {'title': _('Position')},
            'DueDate': {'title': _('Due Date')},
            'Service': {'title': _('Analysis')},
            'Method': {'title': _('Method')},
            'Result': {'title': _('Result'),
                       'input_width': '6',
                       'input_class': 'ajax_calculate numeric',
                       'sortable': False},
            'Uncertainty': {'title': _('+-')},
            'ResultDM': {'title': _('Dry')},
            'retested': {'title': "<img src='++resource++bika.lims.images/retested.png' title='%s'/>" % _('Retested'),
                         'type':'boolean'},
            'Attachments': {'title': _('Attachments')},
            'Instrument': {'title': _('Instrument')},
            'state_title': {'title': _('State')},
        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'transitions': [{'id':'submit'},
                             {'id':'verify'},
                             {'id':'retract'},
                             {'id':'unassign'}],
             'columns':['Pos',
                        'Service',
                        'Method',
                        'Instrument',
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
            pos = [int(slot['position']) for slot in layout if
                   slot['analysis_uid'] == obj.UID()][0]
            highest_position = max(highest_position, pos)
            items[x]['Pos'] = pos
            items[x]['colspan'] = {'Pos':1}
            service = obj.getService()
            method = service.getMethod()
            items[x]['Service'] = service.Title()
            #items[x]['Method'] = method and method.Title() or ''
            items[x]['class']['Service'] = 'service_title'
            items[x]['Category'] = service.getCategory() and service.getCategory().Title() or ''
            if obj.portal_type == "ReferenceAnalysis":
                items[x]['DueDate'] = self.ulocalized_time(obj.aq_parent.getExpiryDate(), long_format=0)
            else:
                items[x]['DueDate'] = self.ulocalized_time(obj.getDueDate())

            items[x]['Order'] = ''
            instrument = obj.getInstrument()
            #items[x]['Instrument'] = instrument and instrument.Title() or ''

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
                    'state_title': 's',})
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

            # set Pos column for this row, to have a rowspan
            # Analysis Remarks only allowed for Analysis types
            # Needs to look inside all slot analyses, cause some of them can
            # have remarks entered and can have different analysis statuses
            rowspan = len(pos_items)
            remarksenabled = self.context.bika_setup.getEnableAnalysisRemarks()
            for pos_subitem in pos_items:
                subitem = items[pos_subitem]
                isanalysis = subitem['obj'].portal_type == 'Analysis'
                hasremarks = True if subitem.get('Remarks', '') else False
                remarksedit = remarksenabled and 'Remarks' in subitem.get('allow_edit', [])
                if isanalysis and (hasremarks or remarksedit):
                    rowspan += 1
            items[x]['rowspan'] = {'Pos': rowspan}

            obj = items[x]['obj']
            # fill the rowspan with a little table
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

            if obj.portal_type == 'ReferenceAnalysis':
                pos_text += "<td class='pos_top'>%s</td>" % obj.getReferenceAnalysesGroupID()
            elif obj.portal_type == 'DuplicateAnalysis' and \
                obj.getAnalysis().portal_type == 'ReferenceAnalysis':
                pos_text += "<td class='pos_top'><a href='%s'>%s</a></td>" % \
                    (obj.aq_parent.absolute_url(), obj.aq_parent.id)
            elif client:
                pos_text += "<td class='pos_top'><a href='%s'>%s</a></td>" % \
                    (client.absolute_url(), client.Title())
            else:
                pos_text += "<td class='pos_top'>&nbsp;</td>"

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
            elif obj.portal_type == 'DuplicateAnalysis':
                pos_text += "<a style='white-space:nowrap' href='%s'>%s</a>" % (obj.getAnalysis().aq_parent.absolute_url(), obj.getReferenceAnalysesGroupID())
            elif parent.portal_type == 'Worksheet':
                parent = obj.getAnalysis().aq_parent
                pos_text += "<a href='%s'>(%s)</a>" % (parent.absolute_url(), parent.Title())
            pos_text += "</td></tr>"

            # sampletype
            pos_text += "<tr><td>"
            if obj.portal_type == 'Analysis':
                pos_text += obj.aq_parent.getSample().getSampleType().Title()
            elif obj.portal_type == 'ReferenceAnalysis' or \
                (obj.portal_type == 'DuplicateAnalysis' and \
                 obj.getAnalysis().portal_type == 'ReferenceAnalysis'):
                pos_text += "" #obj.aq_parent.getReferenceDefinition().Title()
            elif obj.portal_type == 'DuplicateAnalysis':
                pos_text += obj.getAnalysis().aq_parent.getSample().getSampleType().Title()
            pos_text += "</td></tr>"

            # samplingdeviation
            if obj.portal_type == 'Analysis':
                deviation = obj.aq_parent.getSample().getSamplingDeviation()
                if deviation:
                    pos_text += "<tr><td>&nbsp;</td>"
                    pos_text += "<td colspan='2'>"
                    pos_text += deviation.Title()
                    pos_text += "</td></tr>"

##            # barcode
##            barcode = parent.id.replace("-", "")
##            if obj.portal_type == 'DuplicateAnalysis':
##                barcode += "D"
##            pos_text += "<tr><td class='barcode' colspan='3'><div id='barcode_%s'></div>" % barcode + \
##                "<script type='text/javascript'>$('#barcode_%s').barcode('%s', 'code128', {'barHeight':15, addQuietZone:false, showHRI: false })</script>" % (barcode, barcode) + \
##                "</td></tr>"

            pos_text += "</table>"

            items[x]['replace']['Pos'] = pos_text

        for k,v in self.columns.items():
            self.columns[k]['sortable'] = False

        return items

class ManageResultsView(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/worksheet_manage_results.pt")
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.getAnalysts = getUsers(context, ['Manager', 'LabManager', 'Analyst'])

    def __call__(self):
        self.icon = self.portal_url + "/++resource++bika.lims.images/worksheet_big.png"

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

            ws = self.context
            tool = getToolByName(self.context, REFERENCE_CATALOG)
            if analysis_uid:
                analysis = tool.lookupObject(analysis_uid)
                attachment = _createObjectByType("Attachment", ws, tmpID())
                attachment.edit(
                    AttachmentFile=this_file,
                    AttachmentType=self.request.get('AttachmentType', ''),
                    AttachmentKeys=self.request['AttachmentKeys'])
                attachment.reindexObject()

                others = analysis.getAttachment()
                attachments = []
                for other in others:
                    attachments.append(other.UID())
                attachments.append(attachment.UID())
                analysis.setAttachment(attachments)

            if service_uid:
                workflow = getToolByName(self.context, 'portal_workflow')
                for analysis in self.context.getAnalyses():
                    if analysis.portal_type not in ('Analysis', 'DuplicateAnalysis'):
                        continue
                    if not analysis.getServiceUID() == service_uid:
                        continue
                    review_state = workflow.getInfoFor(analysis, 'review_state', '')
                    if not review_state in ['assigned', 'sample_received', 'to_be_verified']:
                        continue

                    attachment = _createObjectByType("Attachment", ws, tmpID())
                    attachment.edit(
                        AttachmentFile = this_file,
                        AttachmentType = self.request.get('AttachmentType', ''),
                        AttachmentKeys = self.request['AttachmentKeys'])
                    attachment.processForm()
                    attachment.reindexObject()

                    others = analysis.getAttachment()
                    attachments = []
                    for other in others:
                        attachments.append(other.UID())
                    attachments.append(attachment.UID())
                    analysis.setAttachment(attachments)

        # Here we create an instance of WorksheetAnalysesView
        self.Analyses = WorksheetAnalysesView(self.context, self.request)
        self.analystname = getAnalystName(self.context)
        self.instrumenttitle = self.context.getInstrument() and self.context.getInstrument().Title() or ''

        # Check if the instruments used are valid
        self.checkInstrumentsValidity()

        return self.template()

    def getInstruments(self):
        # TODO: Return only the allowed instruments for at least one contained analysis
        bsc = getToolByName(self, 'bika_setup_catalog')
        items = [('', '')] + [(o.UID, o.Title) for o in
                               bsc(portal_type = 'Instrument',
                                   inactive_state = 'active')]
        o = self.context.getInstrument()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x, y: cmp(x[1].lower(), y[1].lower()))
        return DisplayList(list(items))

    def isAssignmentAllowed(self):
        checkPermission = self.context.portal_membership.checkPermission
        workflow = getToolByName(self.context, 'portal_workflow')
        review_state = workflow.getInfoFor(self.context, 'review_state', '')
        edit_states = ['open', 'attachment_due', 'to_be_verified']
        return review_state in edit_states \
            and checkPermission(EditWorksheet, self.context)

    def getWideInterims(self):
        """ Returns a dictionary with the analyses services from the current
            worksheet which have at least one interim with 'Wide' attribute
            set to true and state 'sample_received'
            The structure of the returned dictionary is the following:
            <Analysis_keyword>: {
                'analysis': <Analysis_name>,
                'keyword': <Analysis_keyword>,
                'interims': {
                    <Interim_keyword>: {
                        'value': <Interim_default_value>,
                        'keyword': <Interim_key>,
                        'title': <Interim_title>
                    }
                }
            }
        """
        outdict = {}
        allowed_states = ['sample_received']
        for analysis in self.context.getAnalyses():
            wf = getToolByName(analysis, 'portal_workflow')
            if wf.getInfoFor(analysis, 'review_state') not in allowed_states:
                continue

            service = analysis.getService()
            if service.getKeyword() in outdict.keys():
                continue

            calculation = service.getCalculation()
            if not calculation:
                continue

            andict = {'analysis': service.Title(),
                      'keyword': service.getKeyword(),
                      'interims': {}}

            # Analysis Service interim defaults
            for field in service.getInterimFields():
                if field.get('wide', False):
                    andict['interims'][field['keyword']] = field

            # Interims from calculation
            for field in calculation.getInterimFields():
                if field['keyword'] not in andict['interims'].keys() \
                    and field.get('wide', False):
                    andict['interims'][field['keyword']] = field

            if andict['interims']:
                outdict[service.getKeyword()] = andict
        return outdict

    def checkInstrumentsValidity(self):
        """ Checks the validity of the instruments used in the Analyses
            If an analysis with an invalid instrument (out-of-date or
            with calibration tests failed) is found, a warn message
            will be displayed.
        """
        invalid = []
        ans = [a for a in self.context.getAnalyses()]
        for an in ans:
            valid = an.isInstrumentValid()
            if not valid:
                inv = '%s (%s)' % (an.Title(), an.getInstrument().Title())
                if inv not in invalid:
                    invalid.append(inv)
        if len(invalid) > 0:
            message = _("Some analyses use out-of-date or uncalibrated instruments. Results edition not allowed")
            message = "%s: %s" % (message, (', '.join(invalid)))
            self.context.plone_utils.addPortalMessage(message, 'warn')


class AddAnalysesView(BikaListingView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/worksheet_add_analyses.pt")

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/worksheet_big.png"
        self.title = _("Add Analyses")
        self.description = ""
        self.catalog = "bika_analysis_catalog"
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
        self.pagesize = 50

        self.columns = {
            'Client': {
                'title': _('Client'),
                'index':'getClientTitle'},
            'getClientOrderNumber': {
                'title': _('Order'),
                'index': 'getClientOrderNumber'},
            'getRequestID': {
                'title': _('Request ID'),
                'index': 'getRequestID'},
            'CategoryTitle': {
                'title': _('Category'),
                'index':'getCategoryTitle'},
            'Title': {
                'title': _('Analysis'),
                'index':'sortable_title'},
            'getDateReceived': {
                'title': _('Date Received'),
                'index': 'getDateReceived'},
            'getDueDate': {
                'title': _('Due Date'),
                'index': 'getDueDate'},
        }
        self.filter_indexes = ['Title',]
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter': {},
             'transitions': [{'id':'assign'}, ],
             'columns':['Client',
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

        translate = self.context.translate

        form_id = self.form_id
        form = self.request.form
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        if 'submitted' in form:
            if 'getWorksheetTemplate' in form and form['getWorksheetTemplate']:
                layout = self.context.getLayout()
                wst = rc.lookupObject(form['getWorksheetTemplate'])
                self.request['context_uid'] = self.context.UID()
                self.context.applyWorksheetTemplate(wst)
                if len(self.context.getLayout()) != len(layout):
                    self.context.plone_utils.addPortalMessage(
                        to_utf8(translate(PMF("Changes saved."))))
                    self.request.RESPONSE.redirect(self.context.absolute_url() +
                                                   "/manage_results")
                else:
                    self.context.plone_utils.addPortalMessage(
                        to_utf8(translate(_("No analyses were added to this worksheet."))))
                    self.request.RESPONSE.redirect(self.context.absolute_url() +
                                                   "/add_analyses")

        self._process_request()

        if self.request.get('table_only', '') == self.form_id:
            return self.contents_table()
        else:
            return self.template()

    def folderitems(self):
        items = BikaListingView.folderitems(self)
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        hideclientlink = 'RegulatoryInspector' in roles \
            and 'Manager' not in roles \
            and 'LabManager' not in roles \
            and 'LabClerk' not in roles

        for x in range(len(items)):
            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']
            service = obj.getService()
            client = obj.aq_parent.aq_parent
            items[x]['getClientOrderNumber'] = obj.getClientOrderNumber()
            items[x]['getDateReceived'] = self.ulocalized_time(obj.getDateReceived())

            DueDate = obj.getDueDate()
            items[x]['getDueDate'] = self.ulocalized_time(DueDate)
            if DueDate < DateTime():
                items[x]['after']['DueDate'] = '<img width="16" height="16" src="%s/++resource++bika.lims.images/late.png" title="%s"/>' % \
                    (self.context.absolute_url(),
                     to_utf8(self.context.translate(_("Late Analysis"))))
            items[x]['CategoryTitle'] = service.getCategory() and service.getCategory().Title() or ''

            if getSecurityManager().checkPermission(EditResults, obj.aq_parent):
                url = obj.aq_parent.absolute_url() + "/manage_results"
            else:
                url = obj.aq_parent.absolute_url()
            items[x]['getRequestID'] = obj.aq_parent.getRequestID()
            items[x]['replace']['getRequestID'] = "<a href='%s'>%s</a>" % \
                 (url, items[x]['getRequestID'])

            items[x]['Client'] = client.Title()
            if hideclientlink == False:
                items[x]['replace']['Client'] = "<a href='%s'>%s</a>" % \
                    (client.absolute_url(), client.Title())

        hiddenattributes = getHiddenAttributesForClass('AnalysisRequest')
        toggle_cols = self.get_toggle_cols()
        new_states = []
        for i, state in enumerate(self.review_states):
            if state['id'] == self.review_state:
                if hiddenattributes and len(state['columns']) > 0:
                    for field in state['columns']:
                        if field in hiddenattributes:
                            state['columns'].remove(field)
            new_states.append(state)
        self.review_states = new_states
        return items

    def getServices(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        return [c.Title for c in
                bsc(portal_type = 'AnalysisService',
                   getCategoryUID = self.request.get('list_getCategoryUID', ''),
                   inactive_state = 'active',
                   sort_on = 'sortable_title')]

    def getClients(self):
        pc = getToolByName(self.context, 'portal_catalog')
        return [c.Title for c in
                pc(portal_type = 'Client',
                   inactive_state = 'active',
                   sort_on = 'sortable_title')]

    def getCategories(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        return [c.Title for c in
                bsc(portal_type = 'AnalysisCategory',
                   inactive_state = 'active',
                   sort_on = 'sortable_title')]

    def getWorksheetTemplates(self):
        """ Return WS Templates """
        profiles = []
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        return [(c.UID, c.Title) for c in
                bsc(portal_type = 'WorksheetTemplate',
                   inactive_state = 'active',
                   sort_on = 'sortable_title')]

class AddBlankView(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/worksheet_add_control.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/worksheet_big.png"
        self.title = _("Add Blank Reference")
        self.description = _("Select services in the left column to locate "
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
            ref_analyses = self.context.addReferences(position, reference, service_uids)
            self.request.response.redirect(self.context.absolute_url() + "/manage_results")
        else:
            self.Services = WorksheetServicesView(self.context, self.request)
            self.Services.view_url = self.Services.base_url + "/add_blank"
            return self.template()

    def getAvailablePositions(self):
        """ Return a list of empty slot numbers
        """
        layout = self.context.getLayout()
        used_positions = [int(slot['position']) for slot in layout]
        if used_positions:
            available_positions = [pos for pos in range(1, max(used_positions) + 1) if
                                   pos not in used_positions]
        else:
            available_positions = []
        return available_positions

class AddControlView(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/worksheet_add_control.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/worksheet_big.png"
        self.title = _("Add Control Reference")
        self.description = _("Select services in the left column to locate "
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
            ref_analyses = self.context.addReferences(position, reference, service_uids)
            self.request.response.redirect(self.context.absolute_url() + "/manage_results")
        else:
            self.Services = WorksheetServicesView(self.context, self.request)
            self.Services.view_url = self.Services.base_url + "/add_control"
            return self.template()

    def getAvailablePositions(self):
        """ Return a list of empty slot numbers
        """
        layout = self.context.getLayout()
        used_positions = [int(slot['position']) for slot in layout]
        if used_positions:
            available_positions = [pos for pos in range(1, max(used_positions) + 1) if
                                   pos not in used_positions]
        else:
            available_positions = []
        return available_positions

class AddDuplicateView(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/worksheet_add_duplicate.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.icon = self.portal_url + "/++resource++bika.lims.images/worksheet_big.png"
        self.title = _("Add Duplicate")
        self.description = _("Select a destinaton position and the AR to duplicate.")

    def __call__(self):
        if not(getSecurityManager().checkPermission(EditWorksheet, self.context)):
            self.request.response.redirect(self.context.absolute_url())
            return

        form = self.request.form
        if 'submitted' in form:
            ar_uid = self.request.get('ar_uid', '')
            src_slot = [slot['position'] for slot in self.context.getLayout() if
                        slot['container_uid'] == ar_uid and slot['type'] == 'a'][0]
            position = self.request.get('position', '')
            self.request['context_uid'] = self.context.UID()
            self.context.addDuplicateAnalyses(src_slot, position)
            self.request.response.redirect(self.context.absolute_url() + "/manage_results")
        else:
            self.ARs = WorksheetARsView(self.context, self.request)
            return self.template()

    def getAvailablePositions(self):
        """ Return a list of empty slot numbers
        """
        layout = self.context.getLayout()
        used_positions = [int(slot['position']) for slot in layout]
        if used_positions:
            available_positions = [pos for pos in range(1, max(used_positions) + 1) if
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
        self.catalog = 'bika_analysis_catalog'
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
            'created': {'title': _('Date Requested')},
        }
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{},
             'transitions': [],
             'columns':['Position', 'RequestID', 'Client', 'created'],
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
                'created': self.ulocalized_time(ar.created()),
                'replace': {},
                'before': {},
                'after': {},
                'choices':{},
                'class': {},
                'state_class': 'state-active',
                'allow_edit': [],
                'required': [],
            }
            items.append(item)
        items = sorted(items, key = itemgetter('Position'))

        return items

class WorksheetServicesView(BikaListingView):
    """ This table displays a list of services for the adding controls / blanks.
        Services which have analyses in this worksheet are selected, and their
        categories are expanded by default
    """
    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)
        self.context_actions = {}
        self.catalog = 'bika_setup_catalog'
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
            {'id':'default',
             'title': _('All'),
             'contentFilter': {},
             'transitions': [],
             'columns':['Service'],
            },
        ]

    def folderitems(self):
        ws_services = []
        for analysis in self.context.getAnalyses():
            service_uid = analysis.getService().UID()
            if service_uid not in ws_services:
                ws_services.append(service_uid)
        self.categories = []
        catalog = getToolByName(self, self.catalog)
        services = catalog(portal_type = "AnalysisService",
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
                'required': [],
            }
            items.append(item)

        items = sorted(items, key = itemgetter('Service'))
        self.categories.sort(lambda x, y: cmp(x.lower(), y.lower()))

        return items

class ajaxGetWorksheetReferences(ReferenceSamplesView):
    """ Display reference samples matching services in this worksheet
        add_blank and add_control use this to refresh the list of reference
        samples when service checkboxes are selected
    """
    implements(IViewView)

    def __init__(self, context, request):
        super(ajaxGetWorksheetReferences, self).__init__(context, request)
        self.catalog = 'bika_catalog'
        self.contentFilter = {'portal_type': 'ReferenceSample'}
        self.context_actions = {}
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = False
        self.show_workflow_action_buttons = False
        self.pagesize = 50
        # must set service_uids in __call__ before delegating to super
        self.service_uids = []
        # must set control_type='b' or 'c' in __call__ before delegating
        self.control_type = ""
        self.columns['Services'] = {'title': _('Services')}
        self.columns['Definition'] = {'title': _('Reference Definition')}
        self.review_states = [
            {'id':'default',
             'title': _('All'),
             'contentFilter':{'review_state':'current'},
             'columns': ['ID',
                         'Title',
                         'Definition',
                         'ExpiryDate',
                         'Services']
             },
        ]

    def folderitems(self):
        translate = self.context.translate
        workflow = getToolByName(self.context, 'portal_workflow')
        items = super(ajaxGetWorksheetReferences, self).folderitems()
        new_items = []
        for x in range(len(items)):
            if not items[x].has_key('obj'): continue
            obj = items[x]['obj']
            if self.control_type == 'b' and not obj.getBlank(): continue
            if self.control_type == 'c' and obj.getBlank(): continue
            ref_services = obj.getServices()
            ws_ref_services = [rs for rs in ref_services if
                               rs.UID() in self.service_uids]
            if ws_ref_services:
                if workflow.getInfoFor(obj, 'review_state') != 'current':
                    continue
                services = [rs.Title() for rs in ws_ref_services]
                items[x]['nr_services'] = len(services)
                items[x]['Definition'] = (obj.getReferenceDefinition() and obj.getReferenceDefinition().Title()) or ''
                services.sort(lambda x, y: cmp(x.lower(), y.lower()))
                items[x]['Services'] = ", ".join(services)
                items[x]['replace'] = {}

                after_icons = "<a href='%s' target='_blank'><img src='++resource++bika.lims.images/referencesample.png' title='%s: %s'></a>" % \
                    (obj.absolute_url(), \
                     to_utf8(translate(_("Reference sample"))), obj.Title())
                items[x]['before']['ID'] = after_icons

                new_items.append(items[x])

        new_items = sorted(new_items, key = itemgetter('nr_services'))
        new_items.reverse()

        return new_items

    def __call__(self):
        self.service_uids = self.request.get('service_uids', '').split(",")
        self.control_type = self.request.get('control_type', '')
        if not self.control_type:
            return to_utf8(self.context.translate(_("No control type specified")))
        return super(ajaxGetWorksheetReferences, self).contents_table()

class ExportView(BrowserView):
    """
    """
    def __call__(self):

        translate = self.context.translate

        instrument = self.context.getInstrument()
        if not instrument:
            self.context.plone_utils.addPortalMessage(
                to_utf8(translate(_("You must select an instrument"))), 'info')
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        exim = instrument.getDataInterface()
        if not exim:
            self.context.plone_utils.addPortalMessage(
                to_utf8(translate(_("Instrument has no data interface selected"))), 'info')
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        # exim refers to filename in instruments/
        if type(exim) == list:
            exim = exim[0]
        exim = exim.lower()

        # search instruments module for 'exim' module
        if not hasattr(instruments, exim):
            self.context.plone_utils.addPortalMessage(
                to_utf8(translate(_("Instrument exporter not found"))), 'error')
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
        return json.dumps([c.Title for c in
                bsc(portal_type = 'AnalysisService',
                   getCategoryTitle = self.request.get('getCategoryTitle', ''),
                   inactive_state = 'active',
                   sort_on = 'sortable_title')])

class ajaxAttachAnalyses(BrowserView):
    """ In attachment add form,
        the analyses dropdown combo uses this as source.
        Form is handled by the worksheet ManageResults code
    """
    def __call__(self):
        plone.protect.CheckAuthenticator(self.request)
        searchTerm = 'searchTerm' in self.request and self.request['searchTerm'].lower() or ''
        page = self.request['page']
        nr_rows = self.request['rows']
        sord = self.request['sord']
        sidx = self.request['sidx']
        attachable_states = ('assigned', 'sample_received', 'to_be_verified')
        wf = getToolByName(self.context, 'portal_workflow')
        analysis_to_slot = {}
        for s in self.context.getLayout():
            analysis_to_slot[s['analysis_uid']] = int(s['position'])
        analyses = list(self.context.getAnalyses(full_objects=True))
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
                matches = [v for v in row.values()
                           if str(v).lower().startswith(searchTerm)]
                if matches:
                    rows.append(row)

        rows = sorted(rows, cmp=lambda x, y: cmp(x, y), key=itemgetter(sidx and sidx or 'slot'))
        if sord == 'desc':
            rows.reverse()
        pages = len(rows) / int(nr_rows)
        pages += divmod(len(rows), int(nr_rows))[1] and 1 or 0
        start = (int(page)-1) * int(nr_rows)
        end = int(page) * int(nr_rows)
        ret = {'page': page,
               'total': pages,
               'records': len(rows),
               'rows': rows[start:end]}

        return json.dumps(ret)


class ajaxSetAnalyst():
    """The Analysis dropdown sets worksheet.Analyst immediately
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        rc = getToolByName(self.context, 'reference_catalog')
        mtool = getToolByName(self, 'portal_membership')
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)
        value = self.request.get('value', '')
        if not value:
            return
        if not mtool.getMemberById(value):
            return
        self.context.setAnalyst(value)

class ajaxSetInstrument():
    """The Instrument dropdown sets worksheet.Instrument immediately
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        rc = getToolByName(self.context, REFERENCE_CATALOG)
        plone.protect.CheckAuthenticator(self.request)
        plone.protect.PostOnly(self.request)
        value = self.request.get('value', '')
        if not value:
            raise Exception("Invalid instrument")
        instrument = rc.lookupObject(value)
        if not instrument:
            raise Exception("Unable to lookup instrument")
        self.context.setInstrument(instrument)
