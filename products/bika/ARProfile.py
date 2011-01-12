from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.utils import DisplayList
from Products.CMFCore.permissions import View, ListFolderContents
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.bika.BikaContent import BikaSchema
from Products.bika.config import I18N_DOMAIN, ManageBika, PROJECTNAME

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
    ComputedField('ClientUID',
        index = 'FieldIndex',
        expression = 'here.aq_parent.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
),
)

IdField = schema['id']
TitleField = schema['title']
TitleField.required = 0
TitleField.widget.visible = {'edit': 'hidden', 'view': 'invisible'}
    
"""
    AnalysisRequests often use the same configurations.
    ARProfile is used to save these common configurations (templates).
"""
class ARProfile(VariableSchemaSupport, BrowserDefaultMixin, BaseFolder):
    security = ClassSecurityInfo()
    archetype_name = 'ARProfile'
    schema = schema
    immediate_view = 'base_view'
    default_view = 'base_view'
    content_icon = 'arprofile.png' 
    use_folder_tabs = 0
    global_allow = 0
    filter_content_types = 1
    factory_type_information = {
        'title': 'Analysis request profile'
    }
    actions = (
        { 'id': 'view',
          'name': 'View',
          'action': 'string:${object_url}/',
          'permissions': (View,),
          'visible': True,
        },
        { 'id': 'edit',
          'name': 'Edit',
          'action': 'string:${object_url}/arprofile_edit',
          'permissions': (ListFolderContents,),
        },
    )

    def Title(self):
        """ Return the profile title as title """
        return self.getProfileTitle()

    security.declareProtected(View, 'getCatAndServiceUIDs')
    def getCatAndServiceUIDs(self):
        """ Return the categories and services - uids"""
        cats = []
        services = []
        for service in self.getService():
            if service.getCategoryUID() not in cats:
                cats.append(service.getCategoryUID())
            services.append(service.UID())
        results = {'cats': cats,
                   'services': services}
        return results

registerType(ARProfile, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] == 'view':
            a['visible'] = 1
        if a['id'] in ('syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
