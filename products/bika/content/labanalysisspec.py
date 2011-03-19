from AccessControl import ClassSecurityInfo
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.bika.browser.fields import SpecField
from Products.bika.browser.widgets import SpecWidget
from Products.bika.config import I18N_DOMAIN, PROJECTNAME
from Products.bika.content.bikaschema import BikaSchema
import sys

schema = BikaSchema.copy() + Schema((
    ReferenceField('SampleType',
        required = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('SampleType',),
        relationship = 'LabAnalysisSpecSampleType',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = 'Sample Type',
            label_msgid = 'label_type',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    SpecField('ResultsRange',
        required = 1,
        widget = SpecWidget(
            checkbox_bound = 1,
            label = 'Results Range',
            label_msgid = 'label_resultsrange',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ComputedField('SampleTypeUID',
        index = 'FieldIndex',
        expression = 'here.getSampleType().UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
))

schema['title'].required = False
schema['title'].widget.visible = False

class LabAnalysisSpec(BrowserDefaultMixin, BaseContent):
    security = ClassSecurityInfo()
    schema = schema

    def Title(self):
        st = self.getSampleType()
        return st and st.Title() or ''

registerType(LabAnalysisSpec, PROJECTNAME)
