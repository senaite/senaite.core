from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View, \
    ModifyPortalContent
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFPlone.utils import safe_unicode
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _

schema = BikaSchema.copy() + Schema((
    StringField('SampleName',
        widget = StringWidget(
            label = _("Sample"),
        )
    ),
    StringField('ClientRef',
        widget = StringWidget(
            label = _("Client Ref"),
        )
    ),
    StringField('ClientRemarks',
        widget = StringWidget(
            label = _("Client Remarks"),
        )
    ),
    StringField('ClientSid',
        widget = StringWidget(
            label = _("Client SID"),
        )
    ),
    StringField('SampleType',
        widget = StringWidget(
            label = _("Sample Type"),
        )
    ),
    StringField('SampleDate',
        widget = StringWidget(
            label = _("Sample Date"),
        )
    ),
    StringField('NoContainers',
        widget = StringWidget(
            label = _("No of containers"),
        )
    ),
    StringField('PickingSlip',
        widget = StringWidget(
            label = _("Picking Slip"),
        )
    ),
    StringField('ReportDryMatter',
        widget = StringWidget(
            label = _("Report as Dry Matter"),
        )
    ),
    LinesField('AnalysisProfile',
        widget = LinesWidget(
            label = _("Analysis Profile"),
        )
    ),
    LinesField('Analyses',
        widget = LinesWidget(
            label = _("Analyses"),
        )
    ),
    LinesField('Remarks',
        widget = LinesWidget(
            label = _("Remarks"),
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
    schema = schema
    displayContentsTab = False

    def Title(self):
        """ Return the Product as title """
        return safe_unicode(self.getSampleName()).encode('utf-8')


atapi.registerType(ARImportItem, PROJECTNAME)
