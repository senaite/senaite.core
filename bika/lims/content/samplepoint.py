from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims.browser import BrowserView
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME
from bika.lims.browser.fields import CoordinateField
from bika.lims.browser.widgets import CoordinateWidget
from bika.lims.browser.fields import DurationField
from bika.lims.browser.widgets import DurationWidget
from bika.lims import PMF, bikaMessageFactory as _
from zope.interface import implements
import json
import plone
import sys

schema = BikaSchema.copy() + Schema((
    CoordinateField('Latitude',
        schemata = 'Location',
        widget=CoordinateWidget(
            label=_("Latitude"),
            description=_("Enter the Sample Point's latitude in degrees 0-90, minutes 0-59, seconds 0-59 and N/S indicator"),
        ),
    ),
    CoordinateField('Longitude',
        schemata = 'Location',
        widget=CoordinateWidget(
            label=_("Longitude"),
            description=_("Enter the Sample Point's longitude in degrees 0-180, minutes 0-59, seconds 0-59 and E/W indicator"),
        ),
    ),
    StringField('Elevation',
        schemata = 'Location',
        widget=StringWidget(
            label=_("Elevation"),
            description=_("The height or depth at which the sample has to be taken"),
        ),
    ),
    DurationField('SamplingFrequency',
        vocabulary_display_path_bound=sys.maxint,
        widget=DurationWidget(
            label=_("Sampling Frequency"),
            description=_("If a sample is taken periodically at this sample point, enter frequency here, e.g. weekly"),
        ),
    ),
    ReferenceField('SampleTypes',
        required = 0,
        multiValued = 1,
        allowed_types = ('SampleType',),
        vocabulary = 'SampleTypesVocabulary',
        relationship = 'SamplePointSampleType',
        widget = ReferenceWidget(
            checkbox_bound = 0,
            label=_("Sample Types"),
            description =_("The list of sample types that can be collected "
                           "at this sample point.  If no sample types are "
                           "selected, then all sample types are available."),
        ),
    ),
    ComputedField(
        'SampleTypeTitle',
        expression="[o.Title() for o in context.getSampleTypes()]",
        widget = ComputedWidget(
            visible=False,
        )
    ),
    BooleanField('Composite',
        default=False,
        widget=BooleanWidget(
            label=_("Composite"),
            description =_(
                "Check this box if the samples taken at this point are 'composite' "
                "and put together from more than one sub sample, e.g. several surface "
                "samples from a dam mixed together to be a representative sample for the dam. "
                "The default, unchecked, indicates 'grab' samples"),
        ),
    ),
    FileField('AttachmentFile',
        widget = FileWidget(
            label=_("Attachment"),
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

    def Title(self):
        return safe_unicode(self.getField('title').get(self)).encode('utf-8')

    def SampleTypesVocabulary(self):
        from bika.lims.content.sampletype import SampleTypes
        return SampleTypes(self, allow_blank=False)

    def setSampleTypes(self, value, **kw):
        """ For the moment, we're manually trimming the sampletype<>samplepoint
            relation to be equal on both sides, here.
            It's done strangely, because it may be required to behave strangely.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        ## convert value to objects
        if value and type(value) == str:
            value = [bsc(UID=value)[0].getObject(),]
        elif value and type(value) in (list, tuple) and type(value[0]) == str:
            value = [bsc(UID=uid)[0].getObject() for uid in value if uid]
        if not type(value) in (list, tuple):
            value = [value,]
        ## Find all SampleTypes that were removed
        existing = self.Schema()['SampleTypes'].get(self)
        removed = existing and [s for s in existing if s not in value] or []
        added = value and [s for s in value if s not in existing] or []
        ret = self.Schema()['SampleTypes'].set(self, value)

        for st in removed:
            samplepoints = st.getSamplePoints()
            if self in samplepoints:
                samplepoints.remove(self)
                st.setSamplePoints(samplepoints)

        for st in added:
            st.setSamplePoints(list(st.getSamplePoints()) + [self,])

        return ret

    def getSampleTypes(self, **kw):
        return self.Schema()['SampleTypes'].get(self)

    def getClientUID(self):
        return self.aq_parent.UID()

registerType(SamplePoint, PROJECTNAME)

def SamplePoints(self, instance=None, allow_blank=True, lab_only=True):
    instance = instance or self
    bsc = getToolByName(instance, 'bika_setup_catalog')
    items = []
    contentFilter = {
        'portal_type'  : 'SamplePoint',
        'inactive_state'  :'active',
        'sort_on' : 'sortable_title'}
    if lab_only:
        lab_path = instance.bika_setup.bika_samplepoints.getPhysicalPath()
        contentFilter['path'] = {"query": "/".join(lab_path), "level" : 0 }
    for sp in bsc(contentFilter):
        items.append((sp.UID, sp.Title))
    items = allow_blank and [['','']] + list(items) or list(items)
    return DisplayList(items)
