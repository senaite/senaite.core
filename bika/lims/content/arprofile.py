"""
    AnalysisRequests often use the same configurations.
    ARProfile is used to save these common configurations (templates).
"""

from AccessControl import ClassSecurityInfo
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims.browser.widgets import ServicesWidget
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
import sys

schema = BikaSchema.copy() + Schema((
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
    ReferenceField('Service',
        required = 1,
        multiValued = 1,
        allowed_types = ('AnalysisService',),
        relationship = 'ARProfileAnalysisService',
        widget = ServicesWidget(
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

class ARProfile(BaseContent):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False


registerType(ARProfile, PROJECTNAME)
