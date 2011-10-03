"""An item on an invoice.

$Id: InvoiceLineItem.py 70 2006-07-16 12:46:10Z rochecompaan $
"""
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.public import *
from bika.lims.config import ManageInvoices
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
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
            label = _("Order number"),
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
    archetype_name = 'InvoiceLineItem'
    schema = schema
    allowed_content_types = ()
    global_allow = 0
    filter_content_types = 1
    use_folder_tabs = 0
    factory_type_information = {
        'title': 'Invoice line item',
        }

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()


registerType(InvoiceLineItem, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('view', 'syndication', 'references',
                       'metadata', 'localroles'):
            a['visible'] = 0
    return fti
