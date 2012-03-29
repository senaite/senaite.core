from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME
from bika.lims.browser.fields import CoordinateField
from bika.lims.browser.widgets import CoordinateWidget
from bika.lims.browser.fields import DurationField
from bika.lims.browser.widgets import DurationWidget
from zope.i18n import translate
from bika.lims import PMF, bikaMessageFactory as _
from zope.interface import implements
import json
import plone
import sys

schema = BikaSchema.copy() + Schema((
    CoordinateField('Latitude',
        schemata = PMF('Location'),
        widget=CoordinateWidget(
            label= _("Latitude"),
            description = _("Enter the Sample Point's latitude in "
                            "degrees 0-90, minutes 0-59, seconds 0-59 and N/S indicator"),
        ),
    ),
    CoordinateField('Longitude',
        schemata = PMF('Location'),
        widget=CoordinateWidget(
            label= _("Longitude"),
            description = _("Enter the Sample Point's longitude in "
                            "degrees 0-180, minutes 0-59, seconds 0-59 and E/W indicator"),
        ),
    ),
    StringField('Elevation',
        schemata = PMF('Location'),
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
    ReferenceField('SampleTypes',
        required = 0,
        multiValued = 1,
        allowed_types = ('SampleType',),
        vocabulary = 'SampleTypes',
        relationship = 'SamplePointSampleType',
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Sample Types"),
            description = _("The list of sample types that can be collected "
                            "at this sample point.  If no sample types are "
                            "selected, then all sample types are available."),
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

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def SampleTypes(self):
        from bika.lims.content.sampletype import SampleTypes
        return SampleTypes(self)

registerType(SamplePoint, PROJECTNAME)

def SamplePoints(self, instance=None):
    instance = instance or self
    bsc = getToolByName(instance, 'bika_setup_catalog')
    items = []
    for sp in bsc(portal_type='SamplePoint',
                  inactive_state='active',
                  sort_on = 'sortable_title'):
        items.append((sp.UID, sp.Title))
    items = [['','']] + list(items)
    return DisplayList(items)
