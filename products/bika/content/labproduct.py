from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View, \
    ModifyPortalContent
from Products.CMFDynamicViewFTI.browserdefault import \
    BrowserDefaultMixin
from Products.Archetypes.public import *
from Products.bika.content.bikaschema import BikaSchema
from Products.bika.FixedPointField import FixedPointField
from Products.bika.config import I18N_DOMAIN, PROJECTNAME
from Products.bika.fixedpoint import FixedPoint

schema = BikaSchema.copy() + Schema((
    TextField('ProductDescription',
        widget = TextAreaWidget(
            label = 'Product description',
            label_msgid = 'label_product_description',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    StringField('Volume',
        widget = StringWidget(
            label_msgid = 'label_volume',
        )
    ),
    StringField('Unit',
        widget = StringWidget(
            label_msgid = 'label_unit',
        )
    ),
    FixedPointField('VAT',
        default_method = 'getDefaultVAT',
        widget = DecimalWidget(
            label = 'VAT %',
            label_msgid = 'label_vat_percentage',
            description = 'Enter percentage value eg. 14',
            description_msgid = 'help_vat_percentage',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    FixedPointField('Price',
        widget = DecimalWidget(
            label = 'Price excluding VAT',
            label_msgid = 'label_price_excluding_vat',
            i18n_domain = I18N_DOMAIN,
        )
    ),
    ComputedField('VATAmount',
        expression = 'context.getVATAmount',
        widget = ComputedWidget(
            label = 'VAT',
            label_msgid = 'label_vat',
            i18n_domain = I18N_DOMAIN,
            visible = {'edit':'hidden', }
        ),
    ),
    ComputedField('TotalPrice',
        expression = 'context.getTotalPrice()',
        widget = ComputedWidget(
            label = 'Total price',
            label_msgid = 'label_totalprice',
            i18n_domain = I18N_DOMAIN,
            visible = {'edit':'hidden', }
        ),
    ),
))

class LabProduct(BrowserDefaultMixin, BaseContent):
    security = ClassSecurityInfo()
    schema = schema

    def getTotalPrice(self):
        """ compute total price """
        price = self.getPrice()
        vat = self.getVAT()
        price = price and price or 0
        vat = vat and vat / 100 or 0
        return price + price * vat

    def getDefaultVAT(self):
        """ return default VAT from bika_settings """
        try:
            vat = self.bika_settings.getVAT()
            return FixedPoint(vat)
        except ValueError:
            return FixedPoint('0')

    security.declarePublic('getVATAmount')
    def getVATAmount(self):
        """ Compute VATAmount
        """
        try:
            return self.getTotalPrice() - self.getPrice()
        except:
            return 0

registerType(LabProduct, PROJECTNAME)
