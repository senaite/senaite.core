from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.CMFCore.permissions import View, ModifyPortalContent
from bika.lims.config import I18N_DOMAIN, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from decimal import Decimal

schema = BikaSchema.copy() + Schema((
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

class LabProduct(BaseContent):
    security = ClassSecurityInfo()
    schema = schema

    def getTotalPrice(self):
        """ compute total price """
        price = Decimal(self.getPrice())
        vat = Decimal(self.getVAT())
        price = price and price or 0
        vat = vat and vat / 100 or 0
        price = price + (price * vat)
        return price.quantize(Decimal('0.00'))

    def getDefaultVAT(self):
        """ return default VAT from bika_setup """
        try:
            vat = self.bika_setup.getVAT()
            return vat
        except ValueError:
            return "0.00"

    security.declarePublic('getVATAmount')
    def getVATAmount(self):
        """ Compute VATAmount
        """
        try:
            vatamount = self.getTotalPrice() - Decimal(self.getPrice())
            return vatamount.quantize(Decimal('0.00'))
        except:
            vatamount = 0
            return vatamount.quantize(Decimal('0.00'))

registerType(LabProduct, PROJECTNAME)
