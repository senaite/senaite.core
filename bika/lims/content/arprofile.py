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
from bika.lims import bikaMessageFactory as _

schema = BikaSchema.copy() + Schema((
    StringField('ProfileKey',
        index = 'FieldIndex',
        widget = StringWidget(
            label = _("Profile Keyword"),
            description = _("The Analysis Profile's keyword is used to uniquely identify "
                            "it in import files. It has to be unique"),
        ),
    ),
    ReferenceField('Service',
        required = 1,
        multiValued = 1,
        allowed_types = ('AnalysisService',),
        relationship = 'ARProfileAnalysisService',
        widget = ServicesWidget(
            label = _("Analyses"),
            description = _("The analyses included in this Analysis Profile, grouped per category"),
        )
    ),
    TextField('Remarks',
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget = TextAreaWidget(
            label = _("Remarks"),
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
schema['description'].widget.visible = True
schema['description'].schemata = 'default'
IdField = schema['id']

class ARProfile(BaseContent):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False


registerType(ARProfile, PROJECTNAME)
