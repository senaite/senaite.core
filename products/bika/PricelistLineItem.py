"""An item on an pricelist.

$Id: PricelistLineItem.py 2298 2010-05-19 09:18:43Z anneline $
"""
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.public import *
from Products.bika.config import I18N_DOMAIN, PROJECTNAME
from Products.bika.FixedPointField import FixedPointField

schema = BaseSchema.copy() + Schema((
    TextField('ItemDescription',
        widget = TextAreaWidget(
            label = 'Description'
        )
    ),
    TextField('CategoryName',
        widget = TextAreaWidget(
            label = 'Description'
        )
    ),
    BooleanField('Accredited',
        default = False,
        widget = BooleanWidget(
            label = "Accredited",
            label_msgid = "label_accredited",
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


class PricelistLineItem(BaseContent):
    security = ClassSecurityInfo()
    archetype_name = 'PricelistLineItem'
    schema = schema
    allowed_content_types = ()
    global_allow = 0
    filter_content_types = 1
    use_folder_tabs = 0
    factory_type_information = {
        'title': 'Pricelist line item',
        }
    actions = ()

registerType(PricelistLineItem, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('view', 'syndication', 'references',
                       'metadata', 'localroles'):
            a['visible'] = 0
    return fti
