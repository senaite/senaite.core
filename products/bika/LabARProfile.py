import sys
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View, \
    ModifyPortalContent
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.bika.content.bikaschema import BikaSchema
from Products.bika.config import I18N_DOMAIN, PROJECTNAME

schema = BikaSchema.copy() + Schema((
    StringField('ProfileTitle',
        required = 1,
        index = 'FieldIndex',
        searchable = True,
        widget = StringWidget(
            label = 'ProfileTitle',
            label_msgid = 'label_profiletitle',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StringField('ProfileKey',
        index = 'FieldIndex',
        widget = StringWidget(
            label = 'Profile Keyword',
            label_msgid = 'label_profile_keyword',
            description = 'The profile identifier',
            description_msgid = 'help_profile_keyword',
        ),
    ),
    StringField('CostCode', #TODO (dropdown like SampleTypes)
        searchable = True,
        widget = StringWidget(
            label = 'Cost code',
            label_msgid = 'label_costcode',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StringField('TextInclusions', #TODO (dropdown like SampleTypes)
        searchable = True,
        widget = StringWidget(
            label = 'Text Inclusions',
            label_msgid = 'label_textinclusions',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ReferenceField('Service',
        required = 1,
        multiValued = 1,
        allowed_types = ('AnalysisService',),
        relationship = 'ARProfileAnalysisService',
        widget = ReferenceWidget(
            label = 'Analyses',
            label_msgid = 'label_analyses',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    TextField('Remarks',
        widget = TextAreaWidget(
            label = 'Remarks',
            label_msgid = 'label_remarks',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
),
)

IdField = schema['id']
TitleField = schema['title']
TitleField.required = 0
TitleField.widget.visible = False

class LabARProfile(BrowserDefaultMixin, BaseContent):
    security = ClassSecurityInfo()
    archetype_name = 'LabARProfile'
    schema = schema
    allowed_content_types = ()
    default_view = 'labarprofile_edit'
    immediate_view = 'labarprofile_edit'
    content_icon = 'service.png'
    global_allow = 0
    filter_content_types = 0
    use_folder_tabs = 0

    actions = (
       {'id': 'edit',
        'name': 'Edit',
        'action': 'string:${object_url}/labarprofile_edit',
        'permissions': (ModifyPortalContent,),
        },
    )

    factory_type_information = {
        'title': 'Lab analysis profile'
    }

    def Title(self):
        return self.getProfileTitle()

    security.declarePublic("getAnalysisServicesIds")
    def getAnalysisServicesIds(self):
        """ returns the IDs of all the analysisServices
            semicolon delimited to allow javascript to 
            easily split up into array 
        """
        analyses = ""
        active = False
        for service in self.getService():
            if (active):
                analyses += ";"
            else:
                active = True
            analyses += service.UID() 
        return analyses

    security.declarePublic('getCategories')
    def getCategories(self): 
        categories = []
        for service in self.getService():
            categories.append(service.getCategoryUID())
        return categories

registerType(LabARProfile, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('view', 'syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
