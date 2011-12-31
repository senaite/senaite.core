"""An item on an pricelist.
"""
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.public import *
from bika.lims.config import PROJECTNAME
from bika.lims import bikaMessageFactory as _

schema = BaseSchema.copy() + Schema((
    TextField('ItemDescription',
        widget = TextAreaWidget(
            default_content_type = 'text/plain',
            allowable_content_types = ('text/plain',),
            label = _("Description")
        )
    ),
    TextField('CategoryTitle',
        widget = TextAreaWidget(
            label = _("Category")
        )
    ),
    BooleanField('Accredited',
        default = False,
        widget = BooleanWidget(
            label = _("Accredited"),
        ),
    ),
    FixedPointField('Subtotal',
        required = 1,
        default = '0.0',
        widget = DecimalWidget(
            label = _("Subtotal"),
        )
    ),
    FixedPointField('VAT',
        required = 1,
        default = '0.0',
        widget = DecimalWidget(
            label = _("VAT"),
        )
    ),
    FixedPointField('Total',
        required = 1,
        default = '0.0',
        widget = DecimalWidget(
            label = _("Total"),
        )
    ),
),
)

class PricelistLineItem(BaseContent):
    security = ClassSecurityInfo()
    schema = schema

registerType(PricelistLineItem, PROJECTNAME)
