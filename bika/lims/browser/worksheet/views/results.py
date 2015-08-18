# coding=utf-8
from plone.app.layout.globals.interfaces import IViewView
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import DisplayList
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import safe_unicode
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implements

from bika.lims import bikaMessageFactory as _
from bika.lims.config import WORKSHEET_LAYOUT_OPTIONS
from bika.lims.utils import t
from bika.lims.browser import BrowserView
from bika.lims.browser.worksheet.tools import checkUserAccess
from bika.lims.browser.worksheet.tools import showRejectionMessage
from bika.lims.browser.worksheet.views import AnalysesTransposedView
from bika.lims.browser.worksheet.views import AnalysesView
from bika.lims.utils import getUsers, tmpID


class ManageResultsView(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("../templates/results.pt")
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.getAnalysts = getUsers(context, ['Manager', 'LabManager', 'Analyst'])
        self.layout_displaylist = WORKSHEET_LAYOUT_OPTIONS

    def __call__(self):
        # Deny access to foreign analysts
        if checkUserAccess(self.context, self.request) == False:
            return []

        showRejectionMessage(self.context)

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

        # Save the results layout
        rlayout = self.request.get('resultslayout', '')
        if rlayout and rlayout in WORKSHEET_LAYOUT_OPTIONS.keys() \
            and rlayout != self.context.getResultsLayout():
            self.context.setResultsLayout(rlayout)
            message = _("Changes saved.")
            self.context.plone_utils.addPortalMessage(message, 'info')

        # Here we create an instance of WorksheetAnalysesView
        if self.context.getResultsLayout() == '2':
            # Transposed view
            self.Analyses = AnalysesTransposedView(self.context, self.request)
        else:
            # Classic view
            self.Analyses = AnalysesView(self.context, self.request)

        self.analystname = self.context.getAnalystName()
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
        workflow = getToolByName(self.context, 'portal_workflow')
        review_state = workflow.getInfoFor(self.context, 'review_state', '')
        edit_states = ['open', 'attachment_due', 'to_be_verified']
        return review_state in edit_states \
            and self.context.checkUserManage()

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
                inv = '%s (%s)' % (safe_unicode(an.Title()), safe_unicode(an.getInstrument().Title()))
                if inv not in invalid:
                    invalid.append(inv)
        if len(invalid) > 0:
            message = _("Some analyses use out-of-date or uncalibrated instruments. Results edition not allowed")
            message = "%s: %s" % (message, (', '.join(invalid)))
            self.context.plone_utils.addPortalMessage(message, 'warn')

    def getPriorityIcon(self):
        priority = self.context.getPriority()
        if priority:
            icon = priority.getBigIcon()
            if icon:
                return '/'.join(icon.getPhysicalPath())
