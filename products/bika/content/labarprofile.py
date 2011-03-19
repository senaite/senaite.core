from AccessControl import ClassSecurityInfo
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.bika.browser.widgets import ServicesWidget
from Products.bika.config import I18N_DOMAIN, PROJECTNAME
from Products.bika.content.bikaschema import BikaSchema
import sys

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
    StringField('CostCode', #XXX CostCode gets dropdown like SampleTypes
        searchable = True,
        widget = StringWidget(
            label = 'Cost code',
            label_msgid = 'label_costcode',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StringField('TextInclusions', #XXX TextInclusions gets dropdown like SampleTypes
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
        widget = ServicesWidget(
            label = 'Analysis Services',
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
TitleField.required = False
TitleField.widget.visible = False

class LabARProfile(BrowserDefaultMixin, BaseContent):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    def Title(self): #XXX Please will I ever understand this?
        return self.getProfileTitle()

registerType(LabARProfile, PROJECTNAME)
