"""
    AnalysisRequests often use the same configurations.
    AnalysisProfile is used to save these common configurations (templates).
"""

from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import AnalysisProfileAnalysesWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from Products.Archetypes.public import *
from bika.lims.interfaces import IAnalysisProfile
from zope.interface import implements

ProfileKey = StringField(
    'ProfileKey',
    widget=StringWidget(
        label=_("Profile Keyword"),
        description=_(
            "The profile's keyword is used to uniquely identify "
            "it in import files. It has to be unique, and it may "
            "not be the same as any Calculation Interim field ID."),
    ),
)

Service = ReferenceField(
    'Service',
    schemata='Analyses',
    required=1,
    multiValued=1,
    allowed_types=('AnalysisService',),
    relationship='AnalysisProfileAnalysisService',
    widget=AnalysisProfileAnalysesWidget(
        label=_("Profile Analyses"),
        description=_(
            "The analyses included in this profile, grouped per category"),
    )
)

Remarks = TextField(
    'Remarks',
    searchable=True,
    default_content_type='text/plain',
    allowable_content_types=('text/plain', ),
    default_output_type="text/plain",
    widget=TextAreaWidget(
        macro="bika_widgets/remarks",
        label=_("Remarks"),
        append_only=True,
    ),
)

schema = BikaSchema.copy() + Schema((
    ProfileKey,
    Service,
    Remarks
))
schema['title'].widget.visible = True
schema['description'].widget.visible = True
IdField = schema['id']


class AnalysisProfile(BaseContent):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False
    implements(IAnalysisProfile)

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation

        renameAfterCreation(self)

    def getClientUID(self):
        return self.aq_parent.UID()


registerType(AnalysisProfile, PROJECTNAME)
