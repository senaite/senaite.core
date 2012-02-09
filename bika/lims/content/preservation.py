from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import DurationField
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.widgets import DurationWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME, PRESERVATION_CATEGORIES
from Products.Archetypes.references import HoldingReference
import sys


schema = BikaSchema.copy() + Schema((
    StringField('Category',
        default='lab',
        vocabulary=PRESERVATION_CATEGORIES,
        widget=SelectionWidget(
            format='flex',
            label=_('Preservation Category'),
        ),
    ),
    DurationField('RetentionPeriod',
        widget=DurationWidget(
            label=_('Retention period'),
            description=_('Once preserved, the sample must be disposed of within this time period.  If not specified, the sample type retention period will be used.')
        ),
    ),
    ReferenceField('ContainerType',
        required = 0,
        multiValued = 1,
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('ContainerType',),
        vocabulary = 'ContainerTypes',
        relationship = 'PreservationContainerType',
        referenceClass = HoldingReference,
        widget = MultiSelectionWidget(
            format = "select",
            size = 5,
            label = _("Container Type"),
            description=_("Preservation Container Type description",
                          "This preservation requires the sample partition to be stored in one of these container types. Choose multiple values by holding CTRL and clicking.")
        ),
    ),
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'

class Preservation(BaseContent):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    security.declarePublic('ContainerTypes')
    def ContainerTypes(self, instance=None):
        instance = instance or self
        bsc = getToolByName(instance, 'bika_setup_catalog')
        items = bsc(portal_type='ContainerType', sort_on = 'sortable_title')
        return DisplayList(( [(c.UID,c.title) for c in items]))

registerType(Preservation, PROJECTNAME)
