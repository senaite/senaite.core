"""
    AnalysisRequests often use the same configurations.
    ARTemplate includes all AR fields, including preset ARProfile
"""

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from bika.lims import PMF, bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from zope.interface import Interface, implements
import sys

schema = BikaSchema.copy() + Schema((
    ReferenceField('ARProfile',
        required = 1,
        multiValued = 0,
        allowed_types = ('ARProfile',),
        vocabulary = 'ARProfiles',
        relationship = 'ARTemplateARProfile',
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Analysis Profile"),
            description = _("The AR Profile selection for this template"),
        ),
    ),
    ReferenceField('SampleType',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('SampleType',),
        relationship = 'ARTemplateSampleType',
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
        relationship = 'ARTemplateSamplePoint',
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
),
)
schema['title'].widget.visible = True
schema['description'].widget.visible = True
IdField = schema['id']

class ARTemplate(BaseContent):
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
            items.append((st.Title, st.Title))
        items = [['','']] + list(items)
        return DisplayList(items)

    security.declarePublic('SamplePoints')
    def SamplePoints(self, instance=None):
        instance = instance or self
        bsc = getToolByName(instance, 'bika_setup_catalog')
        items = []
        for sp in bsc(portal_type='SamplePoint',
                      inactive_state='active',
                      sort_on = 'sortable_title'):
            items.append((sp.Title, sp.Title))
        items = [['','']] + list(items)
        return DisplayList(items)

    security.declarePublic('ARProfiles')
    def ARProfiles(self, instance=None):
        instance = instance or self
        bsc = getToolByName(instance, 'bika_setup_catalog')
        items = []
        for p in bsc(portal_type='ARProfile',
                      inactive_state='active',
                      sort_on = 'sortable_title'):
            p = p.getObject()
            title = p.Title()
            items.append((p.UID(), title))
        items = [['','']] + list(items)
        return DisplayList(items)

registerType(ARTemplate, PROJECTNAME)
