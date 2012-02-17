"""
    AnalysisRequests often use the same configurations.
    ARProfile is used to save these common configurations (templates).
"""

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims import PMF, bikaMessageFactory as _
from bika.lims.browser.widgets import ServicesWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from zope.interface import Interface, implements
import sys

schema = BikaSchema.copy() + Schema((
    StringField('ProfileKey',
        schemata = PMF('Description'),
        widget = StringWidget(
            label = _("Profile Keyword"),
            description = _("The profile's keyword is used to uniquely identify "
                            "it in import files. It has to be unique, and it may "
                            "not be the same as any Calculation Interim field ID."),
        ),
    ),
    ReferenceField('Service',
        schemata = PMF('Analyses'),
        required = 1,
        multiValued = 1,
        allowed_types = ('AnalysisService',),
        relationship = 'ARProfileAnalysisService',
        widget = ServicesWidget(
            label = _("Profile Analyses"),
            description = _("The analyses included in this profile, grouped per category"),
        )
    ),
    TextField('Remarks',
        schemata = PMF('Description'),
        default_content_type = 'text/plain',
        allowable_content_types = ('text/plain',),
        widget = TextAreaWidget(
            label = _("Remarks"),
        ),
    ),
    ComputedField('ClientTitle',
        expression = 'context.aq_parent.Title()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ClientUID',
        expression = 'context.aq_parent.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
),
)
schema['title'].widget.visible = True
schema['title'].schemata = PMF('Description')
schema['description'].widget.visible = True
schema['description'].schemata = PMF('Description')
IdField = schema['id']

class ARProfile(BaseContent):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(ARProfile, PROJECTNAME)
