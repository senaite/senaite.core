"""An item on an invoice.

$Id: InvoiceLineItem.py 70 2006-07-16 12:46:10Z rochecompaan $
"""
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.public import *
from bika.lims.config import ManageInvoices
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget

schema = BaseSchema.copy() + Schema((
    DateTimeField('ItemDate',
        required = 1,
        default_method = 'current_date',
        widget = DateTimeWidget(
            label = 'Date',
            label_msgid = 'label_date',
        ),
    ),
    StringField('ItemDescription',
        default = '',
        searchable = 1,
        widget = StringWidget(
            label = 'Description',
            label_msgid = 'label_description',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    StringField('ClientOrderNumber',
        index = 'FieldIndex',
        searchable = 1,
        widget = StringWidget(
            label = 'Order number',
            label_msgid = 'label_ordernumber',
            i18n_domain = I18N_DOMAIN,
        ),
    ),

    FixedPointField('Subtotal',
        required = 1,
        default = '0.0',
        widget = DecimalWidget(
            label = 'Subtotal',
            label_msgid = 'label_subtotal',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    FixedPointField('VAT',
        required = 1,
        default = '0.0',
        widget = DecimalWidget(
            label = 'VAT',
            label_msgid = 'label_vat',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    FixedPointField('Total',
        required = 1,
        default = '0.0',
        widget = DecimalWidget(
            label = 'Total',
            label_msgid = 'label_total',
            i18n_domain = I18N_DOMAIN,
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
