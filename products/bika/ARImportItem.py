from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View, \
    ModifyPortalContent
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.bika.BikaContent import BikaSchema
from Products.bika.config import I18N_DOMAIN, PROJECTNAME
from Products.bika.FixedPointField import FixedPointField

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
    archetype_name = 'ARImportItem'
    schema = schema
    allowed_content_types = ('',)
    immediate_view = 'base_view'
    content_icon = 'ar.png'
    global_allow = 0
    filter_content_types = 0
    use_folder_tabs = 0
    actions = (
        { 'id': 'view',
          'visible': False,
        },
        { 'id': 'edit',
          'name': 'Edit',
          'action': 'string:${object_url}/arimportitem_edit',
          'permissions': (ModifyPortalContent,),
          'visible': True,
        },

    )

    def Title(self):
        """ Return the Product as title """
        return  self.getSampleName()
    
registerType(ARImportItem, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
