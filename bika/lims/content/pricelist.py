from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from Products.Archetypes.public import *
from Products.CMFCore import permissions
from bika.lims import bikaMessageFactory as _
from bika.lims.config import ManagePricelists, ManageBika, PRICELIST_TYPES, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.browser.widgets.datetimewidget import DateTimeWidget
from bika.lims.interfaces import IPricelist
from zope.interface import implements
import sys
from plone.app.folder import folder
from bika.lims.content.bikaschema import BikaFolderSchema


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
            label=_('Remarks'),
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
Field.required = 1
Field.widget.visible = True

Field = schema['expirationDate']
Field.schemata = 'default'
Field.required = 1
Field.widget.visible = True


def apply_discount(price=None, discount=None):
    return float(price) - (float(price) * float(discount)) / 100


def get_vat_amount(price, vat_perc):
    return float(price) * float(vat_perc)/100


def create_price_list(instance):
    """ Create price list line items
    """
    # Remove existing line items
    instance.manage_delObjects(instance.objectIds())

    for p in instance.portal_catalog(portal_type=instance.getType(),
                                     inactive_state="active"):
        obj = p.getObject()
        item_id = obj.generateUniqueId("PricelistLineItem")
        instance.invokeFactory(id=item_id, type_name="PricelistLineItem")
        item = instance._getOb(item_id)
        itemDescription = None
        itemAccredited = False
        if instance.getType() == "LabProduct":
            if obj.getVolume() or obj.getUnit():
                print_detail = " ("
            if obj.getVolume():
                print_detail = print_detail + str(obj.getVolume())
            if obj.getUnit():
                print_detail = print_detail + str(obj.getUnit())
            if print_detail:
                print_detail = print_detail + ")"
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

        item.unmarkCreationFlag()
        item.edit(
            title=itemTitle,
            ItemDescription=itemDescription,
            Accredited=itemAccredited,
            Subtotal="%0.2f" % price,
            VATTotal="%0.2f" % vat,
            Total="%0.2f" % totalprice,
            CategoryTitle=cat,
        )
    obj.REQUEST.RESPONSE.redirect('base_view')


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

    def processForm(self, data=1, metadata=0, REQUEST=None, values=None):
        """ Override BaseObject.processForm so that we can create
            invoice lineitems once the form is filled in
        """
        BaseFolder.processForm(self, data=data, metadata=metadata,
            REQUEST=REQUEST, values=values)
        create_price_list(self)

registerType(Pricelist, PROJECTNAME)
