from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View, \
    ModifyPortalContent
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.bika.BikaContent import BikaSchema
from Products.bika.config import I18N_DOMAIN, PROJECTNAME
from Products.bika.FixedPointField import FixedPointField
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin

schema = BikaSchema.copy() + Schema((
    ReferenceField('Product',
        required = 1,
        allowed_types = ('LabProduct',),
        relationship = 'OrderItemLabProduct',
        referenceClass = HoldingReference,
        widget = ReferenceWidget(
            label = 'Product',
            label_msgid = 'label_product',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    IntegerField('Quantity',
        required = 1,
        default = '0',
        widget = IntegerWidget(
            label = 'Quantity',
            label_msgid = 'label_price',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    FixedPointField('Price',
        required = 1,
        widget = DecimalWidget(
            label = 'Unit price',
            label_msgid = 'label_price',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    FixedPointField('VAT',
        required = 1,
        widget = DecimalWidget(
            label = 'VAT',
            label_msgid = 'label_vat',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
),
)

class OrderItem(BrowserDefaultMixin, BaseContent):
    security = ClassSecurityInfo()
    archetype_name = 'OrderItem'
    schema = schema
    allowed_content_types = ()
    immediate_view = 'base_view'
    content_icon = 'product.png'
    global_allow = 0
    filter_content_types = 0
    use_folder_tabs = 0

    def Title(self):
        """ Return the Product as title """
        product = self.getProduct()
        if product:
            return product.Title()
        else:
            return ''
    
    security.declareProtected(View, 'getTotal')
    def getTotal(self):
        """ compute total excluding VAT """
        price = self.getPrice()
        if price:
            return self.getPrice() * self.getQuantity()
        else:
            return 0

    security.declareProtected(View, 'getTotalIncludingVAT')
    def getTotalIncludingVAT(self):
        """ Compute Total including VAT """
        price = self.getPrice()
        quantity = self.getQuantity()
        vat = self.getVAT()
        if price and quantity and vat:
            subtotal = price * quantity
            return subtotal * (1 + vat / 100.0)
        else:
            return 0

registerType(OrderItem, PROJECTNAME)

def modify_fti(fti):
    for a in fti['actions']:
        if a['id'] in ('syndication', 'references', 'metadata',
                       'localroles'):
            a['visible'] = 0
    return fti
