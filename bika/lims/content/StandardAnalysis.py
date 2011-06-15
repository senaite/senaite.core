"""StandardAnalysis

$Id: StandardAnalysis.py 914 2007-10-16 19:49:15Z anneline $
"""
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View, \
    ModifyPortalContent
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, STD_TYPES, PROJECTNAME
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin

#try: XXXXXX XXX
#    from BikaCalendar.config import TOOL_NAME as BIKA_CALENDAR_TOOL
#except:
#    pass

schema = BikaSchema.copy() + Schema((
    StringField('StandardAnalysisID',
        required = 1,
        index = 'FieldIndex',
        searchable = True,
        widget = StringWidget(
            label = 'StandardAnalysis ID',
            label_msgid = 'label_requestid',
            description = 'The ID assigned to the standard analysis',
            description_msgid = 'help_standardanalysis_id',
            i18n_domain = I18N_DOMAIN,
            visible = {'edit':'hidden'},
        ),
    ),
    StringField('StandardType',
        vocabulary = STD_TYPES,
        index = 'FieldIndex',
        widget = SelectionWidget(
            label = 'Standard Type',
            label_msgid = 'label_standardtype',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ReferenceField('Service',
        required = 1,
        allowed_types = ('AnalysisService',),
        relationship = 'StandardAnalysisAnalysisService',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            label = 'Analysis service',
            label_msgid = 'label_analysis',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    StringField('Unit',
        widget = StringWidget(
            label_msgid = 'label_unit',
        ),
    ),
    StringField('CalcType',
        widget = StringWidget(
            label = 'Calculation Type',
            label_msgid = 'label_calculationtype',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    StringField('Result',
        widget = StringWidget(
            label = 'Result',
            label_msgid = 'label_result',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    StringField('InterimCalcs',
        widget = StringWidget(
            label = 'Interim Calculations',
            label_msgid = 'label_interim',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    BooleanField('Retested',
        default = False,
        widget = BooleanWidget(
            label = "Retested",
            label_msgid = "label_retested",
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StringField('Uncertainty',
        widget = StringWidget(
            label = 'Uncertainty',
            label_msgid = 'label_uncertainty',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    DateTimeField('DateRequested',
        required = 1,
        default_method = 'current_date',
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Date Requested',
            label_msgid = 'label_daterequested',
            visible = {'edit':'hidden'},
        ),
    ),
    DateTimeField('DateVerified',
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Date Verified',
            label_msgid = 'label_dateverified',
            visible = {'edit':'hidden'},
        ),
    ),
    ComputedField('StandardSampleUID',
        index = 'FieldIndex',
        expression = 'context.aq_parent.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('StandardSupplierUID',
        index = 'FieldIndex',
        expression = 'context.aq_parent.aq_parent.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ServiceUID',
        index = 'FieldIndex',
        expression = 'context.getService().UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
),
)

class StandardAnalysis(VariableSchemaSupport, BrowserDefaultMixin, BaseContent):
    security = ClassSecurityInfo()
    archetype_name = 'StandardAnalysis'
    schema = schema
    allowed_content_types = ()
    immediate_view = 'base_view'
    global_allow = 0
    filter_content_types = 0
    use_folder_tabs = 0
    actions = ()
    def Title(self):
        """ Return the Service ID as title """
        s = self.getService()
        return s and s.Title() or ''

    security.declarePublic('getWorksheet')
    def getWorksheet(self):
        tool = getToolByName(self, REFERENCE_CATALOG)
        worksheet = ''
        uids = [uid for uid in
                tool.getBackReferences(self, 'WorksheetStandardAnalysis')]
        if len(uids) == 1:
            reference = uids[0]
            worksheet = tool.lookupObject(reference.sourceUID)
        return worksheet

    def getInterim(self):
        """ InterimCalcs field is a self-defining field to cater for 
            the number of different types of calculations performed on 
            analyses. 
        """
        interim = {'tv': None,
                   'tf': None,
                   'sm': None,
                   'nm': None,
                   'gm': None,
                   'vm': None, }

        calctype = self.getCalcType()
        if calctype == 't':
            """ 'vol:fac' """
            if self.getInterimCalcs():
                temp = self.getInterimCalcs().split(':')
                interim['tv'] = temp[0]
                interim['tf'] = temp[1]
        if calctype in ['wlt', 'rwt']:
            """ 'vessel:sample:net' """
            if self.getInterimCalcs():
                temp = self.getInterimCalcs().split(':')
                interim['vm'] = temp[0]
                interim['sm'] = temp[1]
                interim['nm'] = temp[2]
        if calctype in ['wl', 'rw']:
            """ 'gross:vessel:net' """
            if self.getInterimCalcs():
                temp = self.getInterimCalcs().split(':')
                interim['gm'] = temp[0]
                interim['vm'] = temp[1]
                interim['nm'] = temp[2]

        return interim

    def setInterim(self, TV = None, TF = None, VM = None, SM = None, NM = None, GM = None):
        """ 
        """
        calctype = self.getCalcType()
        interim = {}
        if calctype == 't':
            """ 'vol:fac' """
            if self.getInterimCalcs():
                temp = self.getInterimCalcs().split(':')
                interim['tv'] = temp[0]
                interim['tf'] = temp[1]
            else:
                interim['tv'] = ''
                interim['tf'] = ''
            if TV:
                interim['tv'] = TV
            if TF:
                interim['tf'] = TF
            interim_values = interim['tv'] + ':' + interim['tf']
            self.setInterimCalcs(interim_values)

        if calctype in ['wlt', 'rwt']:
            """ 'vessel:sample:net' """
            if self.getInterimCalcs():
                temp = self.getInterimCalcs().split(':')
                interim['vm'] = temp[0]
                interim['sm'] = temp[1]
                interim['nm'] = temp[2]
            else:
                interim['vm'] = ''
                interim['sm'] = ''
                interim['nm'] = ''
            if VM:
                interim['vm'] = VM
            if SM:
                interim['sm'] = SM
            if NM:
                interim['nm'] = NM

            interim_values = interim['vm'] + ':' + interim['sm'] + \
                            ':' + interim['nm']
            self.setInterimCalcs(interim_values)

        if calctype in ['rw', 'wl']:
            """ 'gross:vessel:net' """
            if self.getInterimCalcs():
                temp = self.getInterimCalcs().split(':')
                interim['gm'] = temp[0]
                interim['vm'] = temp[1]
                interim['nm'] = temp[2]
            else:
                interim['gm'] = ''
                interim['vm'] = ''
                interim['nm'] = ''
            if GM:
                interim['gm'] = GM
            if VM:
                interim['vm'] = VM
            if NM:
                interim['nm'] = NM

            interim_values = interim['gm'] + ':' + interim['vm'] + \
                            ':' + interim['nm']
            self.setInterimCalcs(interim_values)

    def getTitrationVolume(self):
        if self.getCalcType() in ['t']:
            interim = self.getInterim()
            return interim['tv']
        else:
            return None

    def setTitrationVolume(self, value):
        if value is None:
            self.setInterim(TV = ' ')
        else:
            self.setInterim(TV = value)
        return

    def getTitrationFactor(self):
        if self.getCalcType() in ['t']:
            interim = self.getInterim()
            return interim['tf']
        else:
            return None

    def setTitrationFactor(self, value):
        if value is None:
            self.setInterim(TF = ' ')
        else:
            self.setInterim(TF = value)
        return


    def getSampleMass(self):
        if self.getCalcType() in ['rwt', 'wlt']:
            interim = self.getInterim()
            return interim['sm']
        else:
            return None

    def setSampleMass(self, value):
        if value is None:
            self.setInterim(SM = ' ')
        else:
            self.setInterim(SM = value)
        return

    def getGrossMass(self):
        if self.getCalcType() in ['rw', 'wl']:
            interim = self.getInterim()
            return interim['gm']
        else:
            return None

    def setGrossMass(self, value):
        if value is None:
            self.setInterim(GM = ' ')
        else:
            self.setInterim(GM = value)
        return

    def getNetMass(self):
        if self.getCalcType() in ['rw', 'rwt', 'wl', 'wlt']:
            interim = self.getInterim()
            return interim['nm']
        else:
            return None

    def setNetMass(self, value):
        if value is None:
            self.setInterim(NM = ' ')
        else:
            self.setInterim(NM = value)
        return

    def getVesselMass(self):
        if self.getCalcType() in ['rw', 'rwt', 'wl', 'wlt']:
            interim = self.getInterim()
            return interim['vm']
        else:
            return None

    def setVesselMass(self, value):
        if value is None:
            self.setInterim(VM = ' ')
        else:
            self.setInterim(VM = value)
        return

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

    def workflow_script_verify(self, state_info):
        """ standard analysis """
        self.setDateVerified(DateTime())

registerType(StandardAnalysis, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
