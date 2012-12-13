"""
    AnalysisRequests often use the same configurations.
    ARTemplate includes all AR fields, including preset AnalysisProfile
"""

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.ATExtensions.field.records import RecordsField
from Products.CMFCore.utils import getToolByName
from bika.lims import PMF, bikaMessageFactory as _
from bika.lims.browser.widgets import RecordsWidget as BikaRecordsWidget
from bika.lims.browser.widgets import ARTemplatePartitionsWidget
from bika.lims.browser.widgets import ARTemplateAnalysesWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from zope.interface import Interface, implements
import sys

schema = BikaSchema.copy() + Schema((
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
    RecordsField('Partitions',
        schemata = 'Sample Partitions',
        required = 0,
        type = 'artemplate_parts',
        subfields = ('part_id', 'container_uid', 'preservation_uid'),
        subfield_labels = {'part_id': _('Partition'),
                           'container_uid': _('Container'),
                           'preservation_uid': _('Preservation')},
        default = [{'part_id':'part-1',
                    'container_uid':'',
                    'preservation_uid':''}],
        widget = ARTemplatePartitionsWidget(
            label = _("Sample Partitions"),
            description = _("Configure the sample partitions and preservations "
                            "for this template. Assign analyses to the different "
                            "partitions on the template's Analyses tab"),
        )
    ),
    ReferenceField('AnalysisProfile',
        schemata = 'Analyses',
        required = 0,
        multiValued = 0,
        allowed_types = ('AnalysisProfile',),
        vocabulary = 'AnalysisProfiles',
        relationship = 'ARTemplateAnalysisProfile',
        widget = ReferenceWidget(
            checkbox_bound = 1,
            label = _("Analysis Profile"),
            description = _("The Analysis Profile selection for this template"),
        ),
    ),
    RecordsField('Analyses',
        schemata = 'Analyses',
        required = 0,
        type = 'artemplate_analyses',
        subfields = ('service_uid', 'partition'),
        subfield_labels = {'service_uid': _('Title'),
                           'partition': _('Partition')},
        default = [],
        widget = ARTemplateAnalysesWidget(
            label = _("Analyses"),
            description = _("Select analyses to include in this template"),
        )
    ),
),
)

schema['description'].widget.visible = True
schema['title'].widget.visible = True
schema['title'].validators = ('uniquefieldvalidator',)
# Update the validation layer after change the validator in runtime
schema['title']._validationLayer()

class ARTemplate(BaseContent):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    security.declarePublic('AnalysisProfiles')
    def AnalysisProfiles(self, instance=None):
        instance = instance or self
        bsc = getToolByName(instance, 'bika_setup_catalog')
        items = []
        for p in bsc(portal_type='AnalysisProfile',
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
            items = bsc(portal_type = 'SampleType', title = value)
            if not items:
                msg = _("${sampletype} is not a valid sample type",
                        mapping={'sampletype':value})
                self.plone_utils.addPortalMessage(msg, 'error')
                self.REQUEST.response.redirect(self.absolute_url())
                return False
            uid = items[0].UID
        return self.Schema()['SampleType'].set(self, uid)

    def getSampleType(self, **kw):
        """ retrieve referenced object and return it's title
        """
        item = self.Schema()['SampleType'].get(self)
        return item and item.Title() or ''

    def setSamplePoint(self, value, **kw):
        """ convert object title to UID
        """
        uid = None
        if value:
            # Strip "Lab: " from sample point title
            value = value.replace("%s: " % _("Lab"), '')
            bsc = getToolByName(self, 'bika_setup_catalog')
            items = bsc(portal_type = 'SamplePoint', title = value)
            if not items:
                msg = _("${samplepoint} is not a valid sample point",
                        mapping={'samplepoint':value})
                self.plone_utils.addPortalMessage(msg, 'error')
                self.REQUEST.response.redirect(self.absolute_url())
                return False
            uid = items[0].UID
        return self.Schema()['SamplePoint'].set(self, uid)

    def getSamplePoint(self, **kw):
        """ retrieve referenced object and return it's title
        """
        item = self.Schema()['SamplePoint'].get(self)
        return item and item.Title() or ''

registerType(ARTemplate, PROJECTNAME)
