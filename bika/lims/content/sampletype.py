from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from bika.lims.browser import BrowserView
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.config import PROJECTNAME
from bika.lims.browser.widgets import DurationWidget
from bika.lims.browser.fields import DurationField
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import ISampleType
from magnitude import mg, MagnitudeError
from zope.interface import implements
import json
import plone
import sys

schema = BikaSchema.copy() + Schema((
    DurationField('RetentionPeriod',
        required = 1,
        default_method = 'getDefaultLifetime',
        widget = DurationWidget(
            label=_("Retention Period"),
            description =_(
                "The period for which un-preserved samples of this type can be kept before "
                "they expire and cannot be analysed any further"),
        )
    ),
    BooleanField('Hazardous',
        default = False,
        widget = BooleanWidget(
            label=_("Hazardous"),
            description=_("Samples of this type should be treated as hazardous"),
        ),
    ),
    ReferenceField('SampleMatrix',
        required = 0,
        allowed_types = ('SampleMatrix',),
        vocabulary = 'SampleMatricesVocabulary',
        relationship = 'SampleTypeSampleMatrix',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 0,
            label=_("Sample Matrix"),
        ),
    ),
    StringField('Prefix',
        required = True,
        widget = StringWidget(
            label=_("Sample Type Prefix"),
        ),
    ),
    StringField('MinimumVolume',
        required = 1,
        widget = StringWidget(
            label=_("Minimum Volume"),
            description=_("The minimum sample volume required for analysis eg. '10 ml' or '1 kg'."),
        ),
    ),
    ReferenceField('ContainerType',
        required = 0,
        allowed_types = ('ContainerType',),
        vocabulary = 'ContainerTypesVocabulary',
        relationship = 'SampleTypeContainerType',
        widget = ReferenceWidget(
            checkbox_bound = 0,
            label=_("Default Container Type"),
            description =_(
                "The default container type. New sample partitions "
                "are automatically assigned a container of this "
                "type, unless it has been specified in more details "
                "per analysis service"),
        ),
    ),
    ReferenceField('SamplePoints',
        required = 0,
        multiValued = 1,
        allowed_types = ('SamplePoint',),
        vocabulary = 'SamplePointsVocabulary',
        relationship = 'SampleTypeSamplePoint',
        widget = ReferenceWidget(
            checkbox_bound = 0,
            label=_("Sample Points"),
            description =_("The list of sample points from which this sample "
                           "type can be collected.  If no sample points are "
                           "selected, then all sample points are available."),
        ),
    ),
    ComputedField(
        'SamplePointTitle',
        expression="[o.Title() for o in context.getSamplePoints()]",
        widget = ComputedWidget(
            visibile=False,
        )
    ),
))

schema['description'].schemata = 'default'
schema['description'].widget.visible = True

class SampleType(BaseContent, HistoryAwareMixin):

    implements(ISampleType)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def Title(self):
        return safe_unicode(self.getField('title').get(self)).encode('utf-8')

    def getJSMinimumVolume(self, **kw):
        """Try convert the MinimumVolume to 'ml' or 'g' so that JS has an
        easier time working with it.  If conversion fails, return raw value.
        """
        default = self.Schema()['MinimumVolume'].get(self)
        try:
            mgdefault = default.split(' ', 1)
            mgdefault = mg(float(mgdefault[0]), mgdefault[1])
        except:
            mgdefault = mg(0, 'ml')
        try:
            return str(mgdefault.ounit('ml'))
        except:
            pass
        try:
            return str(mgdefault.ounit('g'))
        except:
            pass
        return str(default)

    def getDefaultLifetime(self):
        """ get the default retention period """
        settings = getToolByName(self, 'bika_setup')
        return settings.getDefaultSampleLifetime()

    def SamplePointsVocabulary(self):
        from bika.lims.content.samplepoint import SamplePoints
        return SamplePoints(self, allow_blank=False)

    def setSamplePoints(self, value, **kw):
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
        ## Find all SamplePoints that were removed
        existing = self.Schema()['SamplePoints'].get(self)
        removed = existing and [s for s in existing if s not in value] or []
        added = value and [s for s in value if s not in existing] or []
        ret = self.Schema()['SamplePoints'].set(self, value)

        for sp in removed:
            sampletypes = sp.getSampleTypes()
            if self in sampletypes:
                sampletypes.remove(self)
                sp.setSampleTypes(sampletypes)

        for sp in added:
            sp.setSampleTypes(list(sp.getSampleTypes()) + [self,])

        return ret

    def getSamplePoints(self, **kw):
        return self.Schema()['SamplePoints'].get(self)

    def SampleMatricesVocabulary(self):
        from bika.lims.content.samplematrix import SampleMatrices
        return SampleMatrices(self, allow_blank=True)

    def ContainerTypesVocabulary(self):
        from bika.lims.content.containertype import ContainerTypes
        return ContainerTypes(self, allow_blank=True)

registerType(SampleType, PROJECTNAME)

def SampleTypes(self, instance=None, allow_blank=False):
    instance = instance or self
    bsc = getToolByName(instance, 'bika_setup_catalog')
    items = []
    for st in bsc(portal_type='SampleType',
                  inactive_state='active',
                  sort_on = 'sortable_title'):
        items.append((st.UID, st.Title))
    items = allow_blank and [['','']] + list(items) or list(items)
    return DisplayList(items)
