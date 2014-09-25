from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import PROJECTNAME
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import IARPriority
from Products.Archetypes import atapi
from Products.Archetypes.public import *
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
    IntegerField('sortKey',
        widget=IntegerWidget(
            label = "Sort Key",
            description = "Numeric value indicating the sort order of objects that are prioritised",
        ),
    ),
    IntegerField('pricePremium',
        widget=IntegerWidget(
            label = "Price Premium Percentage",
            description = "The percentage used to calculate the price for analyses done at this priority",
        ),
    ),
    ImageField('smallIcon',
        widget=ImageWidget(
            label = "Small Icon",
            description = "16x16 pixel icon used for the this priority in listings."
        ),
    ),
    ImageField('bigIcon',
        widget=ImageWidget(
            label = "Big Icon",
            description = "32x32 pixel icon used for the this priority in object views."
        ),
    ),
    BooleanField('isDefault',
        widget=BooleanWidget(
            label = "Default Priority?",
            description = "Check this box if this is the default priority"
        ),
    ),
))

schema['description'].widget.visible = True


class ARPriority(BaseContent):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False
    implements(IARPriority)
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        renameAfterCreation(self)


atapi.registerType(ARPriority, PROJECTNAME)
