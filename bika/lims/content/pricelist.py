from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from bika.lims import bikaMessageFactory as _
from bika.lims.config import ManagePricelists, ManageBika, PRICELIST_TYPES, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from zope.interface import implements
import sys

schema = BikaSchema.copy() + Schema((
    StringField('Type',
        required = 1,
        vocabulary = PRICELIST_TYPES,
        widget = SelectionWidget(
            label = _("Pricelist for"),
        ),
    ),
    BooleanField('BulkDiscount',
        default = False,
        widget = SelectionWidget(
            label = _("Bulk discount applies"),
        ),
    ),
    FixedPointField('BulkPrice',
        widget = DecimalWidget(
            label = _("Discount %"),
            description = _("Enter discount percentage value"),
        ),
    ),
    BooleanField('Descriptions',
        default = False,
        widget = BooleanWidget(
            label = _("Include descriptions"),
            description = _("Select if the descriptions should be included"),
        ),
    ),
    DateTimeField('StartDate',
        required = 1,
        with_time = False,
        default_method = 'current_date',
        widget = DateTimeWidget(
            label = _("Valid from"),
            show_hm = False,
        ),
    ),
    DateTimeField('EndDate',
        required = 1,
        with_time = False,
        default_method = 'current_date',
        widget = DateTimeWidget(
            label = _("Valid until"),
            show_hm = False,
        ),
    ),
    TextField('Remarks',
        searchable = True,
        default_content_type = 'text/plain',
        allowed_content_types= ('text/plain', ),
        default_output_type="text/plain",
        widget = TextAreaWidget(
            macro = "bika_widgets/remarks",
            label = _('Remarks'),
            append_only = True,
        ),
    ),
),
)

class Pricelist(BaseFolder):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()

    security.declareProtected(ManagePricelists, 'create_price_list')
    def create_price_list(self):
        """ Create price list
        """
        for p in self.portal_catalog(portal_type = self.getType()):
            obj = p.getObject()
            item_id = self.generateUniqueId('PricelistLineItem')
            self.invokeFactory(id = item_id, type_name = 'PricelistLineItem')
            item = self._getOb(item_id)
            itemDescription = None
            itemAccredited = False
            if not cmp(self.getType(), 'LabProduct'):
                if str(obj.getVolume()) or obj.getUnit():
                    print_detail = ' ('
                if str(obj.getVolume()):
                    print_detail = print_detail + str(obj.getVolume())
                if str(obj.getUnit()):
                    print_detail = print_detail + str(obj.getUnit())
                if print_detail:
                    print_detail = print_detail + ')'
                    itemTitle = obj.Title() + print_detail
                else:
                    itemTitle = obj.Title()
                if self.getDescriptions():
                    itemDescription = obj.Description()
            else:
                if str(obj.getUnit()):
                    print_detail = ' (' + str(obj.getUnit()) + ')'
                    itemTitle = obj.Title() + print_detail
                else:
                    itemTitle = obj.Title()
                if self.getDescriptions():
                    itemDescription = obj.Description()
                itemAccredited = obj.getAccredited()
            if self.getType() == 'AnalysisService':
                cat = obj.getCategoryTitle()
                if self.getBulkDiscount():
                    if obj.getBulkDiscount():
                        price = obj.getBulkPrice()
                        totalprice = obj.getTotalBulkPrice()
                        vat = totalprice - price
                    else:
                        price = None
                        totalprice = None
                        vat = None
                else:
                    if obj.getPrice():
                        price = obj.getPrice()
                        totalprice = obj.getTotalPrice()
                        vat = totalprice - price
                    else:
                        totalprice = None
                        price = None
                        vat = None
            else:
                cat = None
                if obj.getPrice():
                    price = obj.getPrice()
                    totalprice = obj.getTotalPrice()
                    vat = totalprice - price
                else:
                    price = None
                    totalprice = None
                    vat = None

            if self.getBulkPrice():
                price = price * (100.0 - self.getBulkPrice()) / 100.0
                totalprice = totalprice * (100 - self.getBulkPrice()) / 100.0
                vat = totalprice - price

            item.edit(
                title = itemTitle,
                ItemDescription = itemDescription,
                Accredited = itemAccredited,
                Subtotal = price,
                VAT = vat,
                Total = totalprice,
                CategoryTitle = cat,
            )
            item.processForm()
        self.REQUEST.RESPONSE.redirect('base_view')

    security.declareProtected(permissions.ModifyPortalContent,
                              'processForm')
    def processForm(self, data = 1, metadata = 0, REQUEST = None, values = None):
        """ Override BaseObject.processForm so that we can create
            invoice lineitems once the form is filled in
        """
        BaseFolder.processForm(self, data = data, metadata = metadata,
            REQUEST = REQUEST, values = values)
        self.create_price_list()

registerType(Pricelist, PROJECTNAME)
