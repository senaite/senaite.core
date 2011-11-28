from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.browser.fields import CoordinateField
from bika.lims.browser.widgets import CoordinateWidget
from bika.lims.browser.fields import DurationField
from bika.lims.browser.widgets import DurationWidget
import sys
from bika.lims import bikaMessageFactory as _

schema = BikaSchema.copy() + Schema((
    CoordinateField('Latitude',
        schemata = _('Location'),
        widget=CoordinateWidget(
            label= _("Latitude"),
            description = _("Enter the Sample Point's latitude in "
                "degrees 0-90, minutes 0-59, seconds 0-59 and N/S indicator"),
        ),
    ),
    CoordinateField('Longitude',
        schemata = _('Location'),
        widget=CoordinateWidget(
            label= _("Longitude"),
            description = _("Enter the Sample Point's longitude in "
                "degrees 0-90, minutes 0-59, seconds 0-59 and E/W indicator"),
        ),
    ),
    StringField('Elevation',
        schemata = _('Location'),
        widget=StringWidget(
            label =  _("Elevation"),
            description = _("The height or depth at which the sample has to be taken"),
        ),
    ),
    DurationField('SamplingFrequency',
        vocabulary_display_path_bound=sys.maxint,
        widget=DurationWidget(
            label = _("Sampling Frequency"),
            description = _("If a sample is taken periodically at this sample point, "
                            " enter frequency here, e.g. weekly"),
        ),
    ),
    BooleanField('Composite',
        default=False,
        widget=BooleanWidget(
            label = _("Composite"),
            description = _("Check this box if the samples taken at this point are 'composite' "
                            "and put together from more than one sub sample, e.g. several surface "
                            "samples from a dam mixed together to be a representative sample for the dam. "
                            "The default, unchecked, indicates 'grab' samples"),
        ),
    ),
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'

class SamplePoint(BaseContent, HistoryAwareMixin):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

registerType(SamplePoint, PROJECTNAME)
