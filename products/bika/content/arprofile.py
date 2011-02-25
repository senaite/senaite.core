"""
    AnalysisRequests often use the same configurations.
    ARProfile is used to save these common configurations (templates).
"""

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATContentTypes.content import schemata
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.utils import DisplayList
from Products.CMFCore.permissions import View, ListFolderContents
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.bika.config import I18N_DOMAIN, ManageBika, PROJECTNAME
from Products.bika.content.bikaschema import BikaSchema

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

schema['title'].required = False


class ARProfile(VariableSchemaSupport, BrowserDefaultMixin, BaseFolder):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

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

atapi.registerType(ARProfile, PROJECTNAME)
