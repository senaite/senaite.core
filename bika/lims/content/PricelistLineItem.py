"""An item on an pricelist.

$Id: PricelistLineItem.py 2298 2010-05-19 09:18:43Z anneline $
"""
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.public import *
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
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
            label = _("Description")
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
