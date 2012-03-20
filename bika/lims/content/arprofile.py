"""
    AnalysisRequests often use the same configurations.
    ARProfile is used to save these common configurations (templates).
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
    ReferenceField('SampleType',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('SampleType',),
        relationship = 'ARProfileSampleType',
        referenceClass = HoldingReference,
        vocabulary = 'SampleTypes',
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Sample Type"),
        ),
    ),
    ReferenceField('SamplePoint',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('SamplePoint',),
        relationship = 'ARPRofileSamplePoint',
        referenceClass = HoldingReference,
        vocabulary = 'SamplePoints',
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Sample Point"),
        ),
    ),
    BooleanField('Composite',
        default = False,
        widget = BooleanWidget(
            label = _("Composite"),
        ),
    ),
    BooleanField('InvoiceExclude',
        default = False,
        widget = BooleanWidget(
            label = _('Invoice Exclude'),
            description = _('Select if analyses to be excluded from invoice'),
        ),
    ),
    BooleanField('ReportDryMatter',
        default = False,
        widget = BooleanWidget(
            label = _('Report as Dry Matter'),
            description = _('This result can be reported as dry matter'),
        ),
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
schema['description'].widget.visible = True
IdField = schema['id']

class ARProfile(BaseContent):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    # Rubbish transplanted here from sample.py
    # Forms submit Title Strings which need
    # to be converted to objects somewhere along the way...
    def setSampleType(self, value, **kw):
        """ convert SampleType title to UID
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        sampletype = bsc(portal_type = 'SampleType', Title = value)
        value = sampletype[0].UID
        return self.Schema()['SampleType'].set(self, value)

    # Rubbish transplanted here from sample.py
    # Forms submit Title Strings which need
    # to be converted to objects somewhere along the way...
    def setSamplePoint(self, value, **kw):
        """ convert SamplePoint title to UID
        """
        sp_uid = None
        if value:
            bsc = getToolByName(self, 'bika_setup_catalog')
            samplepoints = bsc(portal_type = 'SamplePoint', Title = value)
            if samplepoints:
                sp_uid = samplepoints[0].UID
        return self.Schema()['SamplePoint'].set(self, sp_uid)

    security.declarePublic('SampleTypes')
    def SampleTypes(self, instance=None):
        instance = instance or self
        bsc = getToolByName(instance, 'bika_setup_catalog')
        items = []
        for st in bsc(portal_type='SampleType',
                      inactive_state='active',
                      sort_on = 'sortable_title'):
            st = st.getObject()
            title = st.Title()
            items.append((st.UID(), title))
        items = [['','']] + list(items)
        return DisplayList(items)

    security.declarePublic('SamplePoints')
    def SamplePoints(self, instance=None):
        instance = instance or self
        bsc = getToolByName(instance, 'bika_setup_catalog')
        items = []
        for st in bsc(portal_type='SamplePoint',
                      inactive_state='active',
                      sort_on = 'sortable_title'):
            st = st.getObject()
            title = st.Title()
            items.append((st.UID(), title))
        items = [['','']] + list(items)
        return DisplayList(items)

registerType(ARProfile, PROJECTNAME)
