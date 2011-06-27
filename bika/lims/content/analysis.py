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
from bika.lims.browser.widgets import RecordsWidget
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
    FixedPointField('VAT',
        widget = DecimalWidget(
            label = 'VAT %',
            label_msgid = 'label_vat',
            description = 'Enter percentage value eg. 14'
        ),
    ),
    FixedPointField('TotalPrice',
        required = 1,
        widget = DecimalWidget(
            label = 'Total price',
            label_msgid = 'label_totalprice',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    ReferenceField('Method',
        allowed_types = ('Method',),
        relationship = 'AnalysisMethod',
        referenceClass = HoldingReference,
    ),
    StringField('AnalysisKey',
    ),
    ReferenceField('DependantAnalysis',
        multiValued = 1,
        allowed_types = ('Analysis',),
        relationship = 'AnalysisAnalysis',
        referenceClass = HoldingReference,
    ),
    BooleanField('ReportDryMatter',
        default = False,
    ),
    RecordsField('InterimFields',
        # subfield values must be the identical twin of Methods.InterimFields.
        type = 'InterimFields',
        subfields = ('name', 'type', 'value', 'unit', 'collapse'),
        subfield_labels = {'name':'Name', 'type':'Type', 'value':'Default', 'unit':'Unit', 'collapse':'Collapse'},
        required_subfields = ('name',),
        widget = RecordsWidget(
            label = 'Method Interim Fields',
            label_msgid = 'label_interim_fields',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    StringField('Result',
    ),
    BooleanField('Retested',
        default = False,
    ),
    StringField('Uncertainty',
    ),
    ComputedField('Category',
        index = 'FieldIndex:brains',
        expression = 'context.Service.getCategoryName()',
    ),
    ComputedField('ClientUID',
        index = 'FieldIndex',
        expression = 'context.aq_parent.aq_parent.UID()',
    ),
    ComputedField('ClientName',
        index = 'FieldIndex:brains',
        expression = 'context.aq_parent.aq_parent.Title()',
    ),
    ComputedField('RequestID',
        index = 'FieldIndex:brains',
        expression = 'context.aq_parent.getRequestID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('DateReceived',
        index = 'FieldIndex:brains',
        expression = 'context.aq_parent.getDateReceived()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ClientOrderNumber',
        index = 'FieldIndex:brains',
        expression = 'context.aq_parent.getClientOrderNumber()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ServiceUID',
        index = 'FieldIndex:brains',
        expression = 'context.getService() and context.getService.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ServiceName',
        index = 'FieldIndex:brains',
        expression = 'context.getService() and context.getService().Title()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('CategoryName',
        index = 'FieldIndex:brains',
        expression = 'context.getService() and context.getService().getCategoryName()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('PointOfCapture',
        index = 'FieldIndex:brains',
        expression = 'context.getService() and context.getService().getPointOfCapture()',
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
        s = self.getService()
        return s and s.Title() or ''

    #def getInterim(self):
        #""" InterimCalcs field is a self-defining field to cater for
            #the number of different types of calculations performed on
            #analyses.
            #Previously the following specific fields held data for some
            #of the calculations. With the increase in complexity and
            #variety, these values are now embedded with others, into the
            #InterimCalcs field.
            #TitrationRequired',
            #TitrationVolume',
            #TitrationFactor',
            #WeightRequired',
            #GrossWeight',
            #NetWeight',
            #ContainerWeight',
            #The Calculation Types are stored in the CalculationType
            #records, to facilitate addition of new types of calculations
            #without having to reload the data.
        #"""
        #interim = {'tv': None,
                   #'tf': None,
                   #'sm': None,
                   #'nm': None,
                   #'gm': None,
                   #'vm': None, }

        #calctype = self.getCalcType()
        #if calctype == 't':
            #""" 'vol:fac' """
            #if self.getInterimCalcs():
                #temp = self.getInterimCalcs().split(':')
                #interim['tv'] = temp[0]
                #interim['tf'] = temp[1]
        #if calctype in ['wlt', 'rwt']:
            #""" 'vessel:sample:net' """
            #if self.getInterimCalcs():
                #temp = self.getInterimCalcs().split(':')
                #interim['vm'] = temp[0]
                #interim['sm'] = temp[1]
                #interim['nm'] = temp[2]
        #if calctype in ['wl', 'rw']:
            #""" 'gross:vessel:net' """
            #if self.getInterimCalcs():
                #temp = self.getInterimCalcs().split(':')
                #interim['gm'] = temp[0]
                #interim['vm'] = temp[1]
                #interim['nm'] = temp[2]

        #return interim

    #def setInterim(self, TV = None, TF = None, VM = None, SM = None, NM = None, GM = None):
        #"""
        #"""
        #calctype = self.getCalcType()
        #interim = {}
        #if calctype == 't':
            #""" 'vol:fac' """
            #if self.getInterimCalcs():
                #temp = self.getInterimCalcs().split(':')
                #interim['tv'] = temp[0]
                #interim['tf'] = temp[1]
            #else:
                #interim['tv'] = ''
                #interim['tf'] = ''
            #if TV:
                #interim['tv'] = str(TV)
            #if TF:
                #interim['tf'] = str(TF)
            #interim_values = interim['tv'] + ':' + interim['tf']
            #self.setInterimCalcs(interim_values)

        #if calctype in ['wlt', 'rwt']:
            #""" 'vessel:sample:net' """
            #if self.getInterimCalcs():
                #temp = self.getInterimCalcs().split(':')
                #interim['vm'] = temp[0]
                #interim['sm'] = temp[1]
                #interim['nm'] = temp[2]
            #else:
                #interim['vm'] = ''
                #interim['sm'] = ''
                #interim['nm'] = ''
            #if VM:
                #interim['vm'] = str(VM)
            #if SM:
                #interim['sm'] = str(SM)
            #if NM:
                #interim['nm'] = str(NM)

            #interim_values = interim['vm'] + ':' + interim['sm'] + \
                            #':' + interim['nm']
            #self.setInterimCalcs(interim_values)

        #if calctype in ['rw', 'wl']:
            #""" 'gross:vessel:net' """
            #if self.getInterimCalcs():
                #temp = self.getInterimCalcs().split(':')
                #interim['gm'] = temp[0]
                #interim['vm'] = temp[1]
                #interim['nm'] = temp[2]
            #else:
                #interim['gm'] = ''
                #interim['vm'] = ''
                #interim['nm'] = ''
            #if GM:
                #interim['gm'] = str(GM)
            #if VM:
                #interim['vm'] = str(VM)
            #if NM:
                #interim['nm'] = str(NM)

            #interim_values = interim['gm'] + ':' + interim['vm'] + \
                            #':' + interim['nm']
            #self.setInterimCalcs(interim_values)

    #def getTitrationVolume(self):
        #if self.getCalcType() in ['t']:
            #interim = self.getInterim()
            #return interim['tv']
        #else:
            #return None

    #def setTitrationVolume(self, value):
        #if value is None:
            #self.setInterim(TV = ' ')
        #else:
            #self.setInterim(TV = value)
        #return

    #def getTitrationFactor(self):
        #if self.getCalcType() in ['t']:
            #interim = self.getInterim()
            #return interim['tf']
        #else:
            #return None

    #def setTitrationFactor(self, value):
        #if value is None:
            #self.setInterim(TF = ' ')
        #else:
            #self.setInterim(TF = value)
        #return


    #def getSampleMass(self):
        #if self.getCalcType() in ['rwt', 'wlt']:
            #interim = self.getInterim()
            #return interim['sm']
        #else:
            #return None

    #def setSampleMass(self, value):
        #if value is None:
            #self.setInterim(SM = ' ')
        #else:
            #self.setInterim(SM = value)
        #return

    #def getGrossMass(self):
        #if self.getCalcType() in ['rw', 'wl']:
            #interim = self.getInterim()
            #return interim['gm']
        #else:
            #return None

    #def setGrossMass(self, value):
        #if value is None:
            #self.setInterim(GM = ' ')
        #else:
            #self.setInterim(GM = value)
        #return

    #def getNetMass(self):
        #if self.getCalcType() in ['rw', 'rwt', 'wl', 'wlt']:
            #interim = self.getInterim()
            #return interim['nm']
        #else:
            #return None

    #def setNetMass(self, value):
        #if value is None:
            #self.setInterim(NM = ' ')
        #else:
            #self.setInterim(NM = value)
        #return

    #def getVesselMass(self):
        #if self.getCalcType() in ['rw', 'rwt', 'wl', 'wlt']:
            #interim = self.getInterim()
            #return interim['vm']
        #else:
            #return None

    #def setVesselMass(self, value):
        #if value is None:
            #self.setInterim(VM = ' ')
        #else:
            #self.setInterim(VM = value)
        #return

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
