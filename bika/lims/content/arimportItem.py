from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View, \
    ModifyPortalContent
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, PROJECTNAME

schema = BikaSchema.copy() + Schema((
    StringField('SampleName',
        widget = StringWidget(
            label = 'Sample',
            label_msgid = 'label_samplename',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    StringField('ClientRef',
        widget = StringWidget(
            label = 'Client Ref',
            label_msgid = 'label_clientref',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    StringField('ClientRemarks',
        widget = StringWidget(
            label = 'Client Remarks',
            label_msgid = 'label_clientremarks',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    StringField('ClientSid',
        widget = StringWidget(
            label = 'Client Sid',
            label_msgid = 'label_clientsid',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    StringField('SampleType',
        widget = StringWidget(
            label = 'Sample Type',
            label_msgid = 'label_sampletype',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    StringField('SampleDate',
        widget = StringWidget(
            label = 'Sample Date',
            label_msgid = 'label_sampledate',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    StringField('NoContainers',
        widget = StringWidget(
            label = 'No of containers',
            label_msgid = 'label_no_containers',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    StringField('PickingSlip',
        widget = StringWidget(
            label = 'Picking Slip',
            label_msgid = 'label_pickingslip',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    StringField('ReportDryMatter',
        widget = StringWidget(
            label = 'Report as Dry Matter',
            label_msgid = 'label_report_dry_matter',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    LinesField('AnalysisProfile',
        widget = LinesWidget(
            label = 'Analysis Profile',
            label_msgid = 'label_analysis_profile',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    LinesField('Analyses',
        widget = LinesWidget(
            label = 'Analyses',
            label_msgid = 'label_analyses',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    LinesField('Remarks',
        widget = LinesWidget(
            label = 'Remarks',
            label_msgid = 'label_remarks',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    ReferenceField('AnalysisRequest',
        allowed_types = ('AnalysisRequest',),
        relationship = 'ARImportItemAnalysisRequest',
    ),
    ReferenceField('Sample',
        allowed_types = ('Sample',),
        relationship = 'ARImportItemSample',
    ),
),
)

class ARImportItem(BaseContent):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    def Title(self):
        """ Return the Product as title """
        return  self.getSampleName()


atapi.registerType(ARImportItem, PROJECTNAME)
