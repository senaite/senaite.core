from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.browser.widgets.datetimewidget import DateTimeWidget
from bika.lims.config import PRICELIST_TYPES, PROJECTNAME
from bika.lims.content.bikaschema import BikaFolderSchema
from bika.lims.interfaces import IPricelist
from DateTime import DateTime
from persistent.mapping import PersistentMapping
from plone.app.folder import folder
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions



schema = BikaFolderSchema.copy() + Schema((
    StringField('Type',
        required=1,
        vocabulary=PRICELIST_TYPES,
        widget=SelectionWidget(
            format='select',
            label=_("Pricelist for"),
        ),
    ),
    BooleanField('BulkDiscount',
        default=False,
        widget=SelectionWidget(
            label=_("Bulk discount applies"),
        ),
    ),
    FixedPointField('BulkPrice',
        widget=DecimalWidget(
            label=_("Discount %"),
            description=_("Enter discount percentage value"),
        ),
    ),
    BooleanField('Descriptions',
        default=False,
        widget=BooleanWidget(
            label=_("Include descriptions"),
            description=_("Select if the descriptions should be included"),
        ),
    ),
    TextField('Remarks',
        searchable=True,
        default_content_type='text/plain',
        allowed_content_types=('text/plain', ),
        default_output_type="text/plain",
        widget=TextAreaWidget(
            macro="bika_widgets/remarks",
            label=_("Remarks"),
            append_only=True,
        ),
    ),
),
)

Field = schema['title']
Field.required = 1
Field.widget.visible = True

Field = schema['effectiveDate']
Field.schemata = 'default'
Field.required = 0 # "If no date is selected the item will be published
                   #immediately."
Field.widget.visible = True

Field = schema['expirationDate']
Field.schemata = 'default'
Field.required = 0 # "If no date is chosen, it will never expire."
Field.widget.visible = True


def apply_discount(price=None, discount=None):
    return float(price) - (float(price) * float(discount)) / 100


def get_vat_amount(price, vat_perc):
    return float(price) * float(vat_perc) / 100


class PricelistLineItem(PersistentMapping):
    pass


class Pricelist(folder.ATFolder):
    implements(IPricelist)
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

    security.declareProtected(permissions.ModifyPortalContent,
                              'processForm')

registerType(Pricelist, PROJECTNAME)


def ObjectModifiedEventHandler(instance, event):
    """ Various types need automation on edit.
    """
    if not hasattr(instance, 'portal_type'):
        return

    if instance.portal_type == 'Pricelist':
        """ Create price list line items
        """
        # Remove existing line items
        instance.pricelist_lineitems = []
        for p in instance.portal_catalog(portal_type=instance.getType(),
                                         inactive_state="active"):
            obj = p.getObject()
            itemDescription = None
            itemAccredited = False
            if instance.getType() == "LabProduct":
                print_detail = ""
                if obj.getVolume():
                    print_detail = print_detail + str(obj.getVolume())
                if obj.getUnit():
                    print_detail = print_detail + str(obj.getUnit())
                if obj.getVolume() or obj.getUnit():
                    print_detail = " (" + print_detail + ")"
                    itemTitle = obj.Title() + print_detail
                else:
                    itemTitle = obj.Title()
                cat = None
                if obj.getPrice():
                    price = float(obj.getPrice())
                    totalprice = float(obj.getTotalPrice())
                    vat = totalprice - price
                else:
                    price = 0
                    totalprice = 0
                    vat = 0
            elif instance.getType() == "AnalysisService":
                #
                if str(obj.getUnit()):
                    print_detail = " (" + str(obj.getUnit()) + ")"
                    itemTitle = obj.Title() + print_detail
                else:
                    itemTitle = obj.Title()
                itemAccredited = obj.getAccredited()
                #
                cat = obj.getCategoryTitle()
                if instance.getBulkDiscount():
                        price = float(obj.getBulkPrice())
                        vat = get_vat_amount(price, obj.getVAT())
                        totalprice = price + vat
                else:
                    if instance.getBulkPrice():
                        discount = instance.getBulkPrice()
                        price = float(obj.getPrice())
                        price = apply_discount(price, discount)
                        vat = get_vat_amount(price, obj.getVAT())
                        totalprice = price + vat
                    elif obj.getPrice():
                        price = float(obj.getPrice())
                        vat = get_vat_amount(price, obj.getVAT())
                        totalprice = price + vat
                    else:
                        totalprice = 0
                        price = 0
                        vat = 0

            if instance.getDescriptions():
                itemDescription = obj.Description()

            li = PricelistLineItem()
            li['title'] = itemTitle
            li['ItemDescription'] = itemDescription
            li['CategoryTitle'] = cat
            li['Accredited'] = itemAccredited
            li['Subtotal'] = "%0.2f" % price
            li['VATAmount'] = "%0.2f" % vat
            li['Total'] = "%0.2f" % totalprice
            instance.pricelist_lineitems.append(li)
