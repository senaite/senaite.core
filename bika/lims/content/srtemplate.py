"""
    Sample Round Template
"""

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.ATExtensions.field.records import RecordsField
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import RecordsWidget as BikaRecordsWidget
# from bika.lims.browser.widgets import ARTemplateAnalysesWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
import sys

schema = BikaSchema.copy() + Schema((
    TextField('Instructions',
        searchable = True,
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain', ),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            # macro = "bika_widgets/remarks",
            label = _('Instructions'),
            append_only = True,
        ),
    ),
    # RecordsField('AR Templates',
    #     schemata = 'AR Templates',
    #     required = 0,
    #     type = 'srtemplate_artemplates',
    #     subfields = ('service_uid', 'partition'),
    #     subfield_labels = {},
    #     default = [],
    #     widget = ARTemplateAnalysesWidget(
    #         label = _("AR Templates"),
    #         description = _("Select AR Templates to include"),
    #     )
    # ),
),
)


schema['description'].widget.visible = True
schema['title'].widget.visible = True
schema['title'].validators = ('uniquefieldvalidator',)
# Update the validation layer after change the validator in runtime
schema['title']._validationLayer()


class SRTemplate(BaseContent):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    # security.declarePublic('AnalysisProfiles')
    # def AnalysisProfiles(self, instance=None):
    #     instance = instance or self
    #     bsc = getToolByName(instance, 'bika_setup_catalog')
    #     items = []
    #     for p in bsc(portal_type='AnalysisProfile',
    #                   inactive_state='active',
    #                   sort_on = 'sortable_title'):
    #         p = p.getObject()
    #         title = p.Title()
    #         items.append((p.UID(), title))
    #     items = [['','']] + list(items)
    #     return DisplayList(items)

registerType(SRTemplate, PROJECTNAME)
