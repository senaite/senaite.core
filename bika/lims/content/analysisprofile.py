"""
    AnalysisRequests often use the same configurations.
    AnalysisProfile is used to save these common configurations (templates).
"""

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from bika.lims import PMF, bikaMessageFactory as _
from bika.lims.browser.widgets import ServicesWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from zope.interface import Interface, implements
import sys

schema = BikaSchema.copy() + Schema((
    StringField('ProfileKey',
        widget = StringWidget(
            label = _("Profile Keyword"),
            description = _("The profile's keyword is used to uniquely identify "
                            "it in import files. It has to be unique, and it may "
                            "not be the same as any Calculation Interim field ID."),
        ),
    ),
    ReferenceField('Service',
        schemata = 'Analyses',
        required = 1,
        multiValued = 1,
        allowed_types = ('AnalysisService',),
        relationship = 'AnalysisProfileAnalysisService',
        widget = ServicesWidget(
            label = _("Profile Analyses"),
            description = _("The analyses included in this profile, grouped per category"),
        )
    ),
    TextField('Remarks',
        searchable = True,
        default_content_type = 'text/x-web-intelligent',
        allowable_content_types = ('text/x-web-intelligent',),
        default_output_type="text/html",
        widget = TextAreaWidget(
            macro = "bika_widgets/remarks",
            label = _('Remarks'),
            append_only = True,
        ),
    ),
),
)
schema['title'].widget.visible = True
schema['description'].widget.visible = True
IdField = schema['id']

class AnalysisProfile(BaseContent):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(AnalysisProfile, PROJECTNAME)
