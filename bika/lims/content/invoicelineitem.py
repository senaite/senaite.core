"""An item on an invoice.
"""
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.public import *
from bika.lims.config import ManageInvoices
from bika.lims.config import PROJECTNAME
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from bika.lims import bikaMessageFactory as _

schema = BaseSchema.copy() + Schema((
    DateTimeField('ItemDate',
        required = 1,
        default_method = 'current_date',
        widget = DateTimeWidget(
            label = _("Date"),
        ),
    ),
    StringField('ItemDescription',
        default = '',
        searchable = 1,
        widget = StringWidget(
            label = _("Description"),
        ),
    ),
    StringField('ClientOrderNumber',
        searchable = 1,
        widget = StringWidget(
            label = _("Order Number"),
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

class InvoiceLineItem(BaseContent):
    security = ClassSecurityInfo()
    security.declareObjectProtected(ManageInvoices)
    displayContentsTab = False
    schema = schema

    security.declarePublic('current_date')
    def current_date(self):
        return DateTime()

registerType(InvoiceLineItem, PROJECTNAME)
