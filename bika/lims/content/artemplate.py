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
    ## SamplePoint and SampleType references are managed with
    ## accessors and mutators below to get/set a string value
    ## (the Title of the object), but still store a normal Reference.
    ## Form autocomplete widgets can then work with the Titles.
    ReferenceField('SamplePoint',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('SamplePoint',),
        relationship = 'ARTemplateSamplePoint',
        referenceClass = HoldingReference,
        accessor = 'getSamplePoint',
        edit_accessor = 'getSamplePoint',
        mutator = 'setSamplePoint',
        widget = StringWidget(
            label = _("Sample Point"),
        ),
    ),
    ReferenceField('SampleType',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('SampleType',),
        relationship = 'ARTemplateSampleType',
        referenceClass = HoldingReference,
        accessor = 'getSampleType',
        edit_accessor = 'getSampleType',
        mutator = 'setSampleType',
        widget = StringWidget(
            label = _("Sample Type"),
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

    def setSampleType(self, value, **kw):
        """ convert object title to UID
        """
        uid = None
        if value:
            bsc = getToolByName(self, 'bika_setup_catalog')
            items = bsc(portal_type = 'SampleType', Title = value)
            if not items:
                msg = _("${sampletype} is not a valid sample type",
                        mapping={'sampletype':value})
                self.context.plone_utils.addPortalMessage(msg, 'error')
                self.destination_url = self.request.get_header("referer",
                                       self.context.absolute_url())
                self.request.response.redirect(self.destination_url)
                return False
            uid = items[0].UID
        return self.Schema()['SampleType'].set(self, uid)

    def getSampleType(self, **kw):
        """ retrieve referenced object and return it's title
        """
        uid = self.Schema()['SampleType'].get(self)
        if not uid:
            return ''
        rc = getToolByName(self, 'uid_catalog')
        items = rc(UID=uid)
        if not items:
            return ''
        return items[0].Title

    def setSamplePoint(self, value, **kw):
        """ convert object title to UID
        """
        uid = None
        if value:
            bsc = getToolByName(self, 'bika_setup_catalog')
            items = bsc(portal_type = 'SamplePoint', Title = value)
            if not items:
                msg = _("${samplepoint} is not a valid sample point",
                        mapping={'samplepoint':value})
                self.context.plone_utils.addPortalMessage(msg, 'error')
                self.destination_url = self.request.get_header("referer",
                                       self.context.absolute_url())
                self.request.response.redirect(self.destination_url)
                return False
            uid = items[0].UID
        return self.Schema()['SamplePoint'].set(self, uid)

    def getSamplePoint(self, **kw):
        """ retrieve referenced object and return it's title
        """
        uid = self.Schema()['SamplePoint'].get(self)
        if not uid:
            return ''
        rc = getToolByName(self, 'uid_catalog')
        items = rc(UID=uid)
        if not items:
            return ''
        return items[0].Title

registerType(ARTemplate, PROJECTNAME)
