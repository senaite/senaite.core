"""Analysis

$Id: Analysis.py 1902 2009-10-10 12:17:42Z anneline $
"""
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View, \
    ModifyPortalContent
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget, RecordsField
from bika.lims.browser.widgets import RecordsWidget as BikaRecordsWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, PROJECTNAME

# XXX XXX tune up

#try:
#    from bika.limsCalendar.config import TOOL_NAME as BIKA_CALENDAR_TOOL # XXX
#except:
#    pass

schema = BikaSchema.copy() + Schema((
    ReferenceField('Service',
        required = 1,
        allowed_types = ('AnalysisService',),
        relationship = 'AnalysisAnalysisService',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            label = 'Analysis service',
            label_msgid = 'label_analysis',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    ComputedField('Category',
        index = 'FieldIndex:brains',
        expression = 'context.Service.getCategoryName()',
    ),

    ReferenceField('Attachment',
        multiValued = 1,
        allowed_types = ('Attachment',),
        referenceClass = HoldingReference,
        relationship = 'AnalysisAttachment',
    ),
    FixedPointField('Price',
        required = 1,
        widget = DecimalWidget(
            label = 'Price',
            label_msgid = 'label_price',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    StringField('Unit',
        widget = StringWidget(
            label_msgid = 'label_unit',
        ),
    ),
    ReferenceField('Calculation',
        allowed_types = ('Calculation',),
        relationship = 'AnalysisCalculation',
        referenceClass = HoldingReference,
    ),
    StringField('Keyword',
    ),
    BooleanField('ReportDryMatter',
        default = False,
    ),
    RecordsField('InterimFields',
        # 'subfields' must be the identical twin of Calculation.InterimFields.
        type = 'InterimFields',
        subfields = ('id', 'title', 'value', 'unit'),
        subfield_labels = {'id':'Field ID', 'title':'Field Title', 'value':'Default', 'unit':'Unit'},
        required_subfields = ('id','title',),
        widget = BikaRecordsWidget(
            label = 'Calculation Interim Fields',
            label_msgid = 'label_interim_fields',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    StringField('Result',
    ),
    BooleanField('Retested',
        default = False,
    ),
    ComputedField('DateReceived',
        index = 'FieldIndex:brains',
        expression = 'context.aq_parent.getDateReceived()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    DateTimeField('DateAnalysisPublished',
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Date published',
            label_msgid = 'label_datepublished',
            visible = {'edit':'hidden'},
        ),
    ),
    IntegerField('MaxHoursAllowed',
        widget = IntegerWidget(
            label = "Maximum Hours Allowed",
        ),
    ),
    DateTimeField('DueDate',
        index = 'DateIndex:brains',
        widget = DateTimeWidget(
            label = 'Due Date'
        ),
    ),
    IntegerField('Duration',
        index = 'FieldIndex',
        widget = IntegerWidget(
            label = 'Duration',
            label_msgid = 'label_duration',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    IntegerField('Earliness',
        index = 'FieldIndex',
        widget = IntegerWidget(
            label = 'Earliness',
            label_msgid = 'label_earliness',
            i18n_domain = I18N_DOMAIN,
        )
    ),

    ###

    ComputedField('ClientUID',
        index = 'FieldIndex',
        expression = 'context.aq_parent.aq_parent.UID()',
    ),
    ComputedField('RequestID',
        index = 'FieldIndex:brains',
        expression = 'context.aq_parent.getRequestID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('PointOfCapture',
        index = 'FieldIndex',
        expression = 'context.getService() and context.getService().getPointOfCapture()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
),
)

class Analysis(BaseContent):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _assigned_to_worksheet = False
    _affects_other_analysis = False

    def Title(self):
        """ Return the service title as title """
        # We construct the analyses manually in ar_add_submit,
        # and they are without Service attribute for a moment.
        s = self.getService()
        if s: return s.Title()

    def getUncertainty(self):
        """ The uncertainty value is calculated from the Service. """
        result = self.getResult()
        uncertainties = self.getService().getUncertainties()

        if not (result and uncertainties):
            return None

        try:
            result = float(result)
        except ValueError:
            # if it is not a float we assume no measure of uncertainty
            return None

        for d in uncertainties:
            if float(d['intercept_min']) <= result < float(d['intercept_max']):
                return d['errorvalue']
        return None

    def checkHigherDependancies(self):
        if self._affects_other_analysis:
            return True
        else:
            return False


    # workflow methods
    #
    def workflow_script_receive(self, state_info):
        """ receive sample """
        if self.REQUEST.has_key('suppress_escalation'):
            return
        """ set the max hours allowed """
        service = self.getService()
        maxhours = service.getMaxHoursAllowed()
        if not maxhours:
            maxhours = 0

        self.setMaxHoursAllowed(maxhours)
        """ set the due date """
        starttime = self.aq_parent.getDateReceived()
        if starttime is None:
            return

        """ default to old calc in case no calendars  """
        """ still need a due time for selection to ws """
        duetime = starttime + maxhours / 24.0

        if maxhours:
            maxminutes = maxhours * 60
            try:
                bct = getToolByName(self, BIKA_CALENDAR_TOOL)
            except:
                bct = None
            if bct:
                duetime = bct.getDurationAdded(starttime, maxminutes)

        self.setDueDate(duetime)
        self.reindexObject()

        self._escalateWorkflowAction('receive')

    def workflow_script_assign(self, state_info):
        """ submit sample """
        self._escalateWorkflowAction('assign')
        self._assigned_to_worksheet = True

    def workflow_script_submit(self, state_info):
        """ submit sample """
        self._escalateWorkflowDependancies('submit')
        self._escalateWorkflowAction('submit')

    def workflow_script_verify(self, state_info):
        """ verify sample """
        self._escalateWorkflowDependancies('verify')
        self._escalateWorkflowAction('verify')

    def workflow_script_publish(self, state_info):
        """ publish analysis """
        starttime = self.aq_parent.getDateReceived()
        endtime = DateTime()
        self.setDateAnalysisPublished(endtime)

        service = self.getService()
        maxhours = service.getMaxHoursAllowed()

        """ set the analysis duration value to default values """
        """ in case of no calendars or max hours """
        if maxhours:
            duration = (endtime - starttime) * 24 * 60
            earliness = (maxhours * 60) - duration
        else:
            earliness = 0
            duration = 0
        try:
            bct = getToolByName(self, BIKA_CALENDAR_TOOL)
        except:
            bct = None
        if bct:
            duration = bct.getDuration(starttime, endtime)
            """ set the earliness of the analysis """
            """ will be negative if late """
            if self.getDueDate():
                earliness = bct.getDuration(endtime, self.getDueDate())

        self.setDuration(duration)
        self.setEarliness(earliness)
        self.reindexObject()
        self._escalateWorkflowAction('publish')

    def workflow_script_retract(self, state_info):
        """ retract analysis """
        self._escalateWorkflowDependancies('retract')
        self._escalateWorkflowAction('retract')
        if self._assigned_to_worksheet:
            self.portal_workflow.doActionFor(self, 'assign')
            self.reindexObject()
            self._escalateWorkflowDependancies('assign')
            self._escalateWorkflowAction('assign')

    def _escalateWorkflowAction(self, action_id):
        """ notify analysis request that our status changed """
        self.aq_parent._escalateWorkflowAction()
        # if we are assigned to a worksheet we need to let it know that
        # our state change under certain circumstances.
        if action_id not in ('assign', 'retract', 'submit', 'verify'):
            return
        tool = getToolByName(self, REFERENCE_CATALOG)
        uids = [uid for uid in
                tool.getBackReferences(self, 'WorksheetAnalysis')]
        if len(uids) == 1:
            reference = uids[0]
            worksheet = tool.lookupObject(reference.sourceUID)
            worksheet._escalateWorkflowAction()

    def _escalateWorkflowDependancies(self, action_id):
        """ notify analysis request that our status changed """
        # if this analysis affects other analysis results, escalate
        # the workflow change appropriately
        if not self._affects_other_analysis:
            return
        if action_id not in ('retract', 'submit', 'verify'):
            return
        if action_id == 'submit':
            ready_states = ['to_be_verified', 'verified', 'published']
        if action_id == 'verify':
            ready_states = ['verified', 'published']
        wf_tool = self.portal_workflow
        tool = getToolByName(self, REFERENCE_CATALOG)
        parents = [uid for uid in
            tool.getBackReferences(self, 'AnalysisAnalysis')]
        for p in parents:
            parent = tool.lookupObject(p.sourceUID)
            parent_state = wf_tool.getInfoFor(parent, 'review_state', '')
            if action_id == 'retract':
                try:
                    wf_tool.doActionFor(parent, 'retract')
                    parent.reindexObject()
                except WorkflowException:
                    pass

            if action_id in ['submit', 'verify']:
                if parent_state in ready_states:
                    continue

                all_ready = True
                for child in parent.getDependantAnalysis():
                    review_state = wf_tool.getInfoFor(child, 'review_state', '')
                    if review_state not in ready_states:
                        all_ready = False
                        break
                if all_ready:
                    try:
                        wf_tool.doActionFor(parent, action_id)
                        parent.reindexObject()
                    except WorkflowException:
                        pass

    security.declarePublic('getWorksheet')
    def getWorksheet(self):
        tool = getToolByName(self, REFERENCE_CATALOG)
        worksheet = ''
        uids = [uid for uid in
                tool.getBackReferences(self, 'WorksheetAnalysis')]
        if len(uids) == 1:
            reference = uids[0]
            worksheet = tool.lookupObject(reference.sourceUID)

        return worksheet


atapi.registerType(Analysis, PROJECTNAME)
