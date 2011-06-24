import sys
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ListFolderContents, \
    ModifyPortalContent, View
from Products.CMFCore import permissions
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.ATExtensions.ateapi import DateTimeField, DateTimeWidget
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.config import I18N_DOMAIN, ManageBika, PROJECTNAME

schema = BikaSchema.copy() + Schema((
    ReferenceField('Contact',
        required = 1,
        vocabulary = 'getContactsDisplayList',
        default_method = 'getContactUIDForUser',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Contact',),
        referenceClass = HoldingReference,
        relationship = 'OrderContact',
    ),
    StringField('OrderNumber',
        required = 1,
        default_method = 'getId',
        index = 'FieldIndex',
        searchable = True,
        widget = StringWidget(
            label = 'Order number',
            label_msgid = 'label_ordernumber',
            i18n_domain = I18N_DOMAIN,
        ),
    ),
    ReferenceField('Invoice',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('Invoice',),
        referenceClass = HoldingReference,
        relationship = 'OrderInvoice',
    ),
    DateTimeField('OrderDate',
        required = 1,
        default_method = 'current_date',
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Date',
            label_msgid = 'label_orderdate',
        ),
    ),
    DateTimeField('DateDispatched',
        index = 'DateIndex',
        widget = DateTimeWidget(
            label = 'Date dispatched',
            label_msgid = 'label_datedispatched',
        ),
    ),
    TextField('Notes',
        widget = TextAreaWidget(
            label = 'Notes'
        )
    ),
    ComputedField('ClientUID',
        index = 'FieldIndex',
        expression = 'here.aq_parent.UID()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ProductUID',
        index = 'KeywordIndex',
        expression = 'context.getProductUIDs()',
        widget = ComputedWidget(
            visible = False,
        ),
    ),
),
)

schema['title'].required = False

class Order(BaseFolder):
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    def hasBeenInvoiced(self):
        if self.getInvoice():
    	    return True
        else:
            return False

    def Title(self):
        """ Return the OrderNumber as title """
        return self.getOrderNumber()


    security.declarePublic('getContactUIDForUser')
    def getContactUIDForUser(self):
        """ get the UID of the contact associated with the authenticated
            user
        """
        user = self.REQUEST.AUTHENTICATED_USER
        user_id = user.getUserName()
        r = self.portal_catalog(
            portal_type = 'Contact',
            getUsername = user_id
        )
        if len(r) == 1:
            return r[0].UID

    security.declareProtected(View, 'getTotalQty')
    def getTotalQty(self):
        """ Compute total qty """
        return sum(
            [obj.getQuantity() \
             for obj in self.objectValues('OrderItem')])

    security.declareProtected(View, 'getSubtotal')
    def getSubtotal(self):
        """ Compute Subtotal """
        return sum(
            [obj.getTotal() \
             for obj in self.objectValues('OrderItem')])

    security.declareProtected(View, 'getVAT')
    def getVAT(self):
        """ Compute VAT """
        return self.getTotal() - self.getSubtotal()

    security.declareProtected(View, 'getTotal')
    def getTotal(self):
        """ Compute TotalPrice """
        return sum(
            [obj.getTotalIncludingVAT() \
             for obj in self.objectValues('OrderItem')])

    def workflow_script_dispatch(self, state_info):
        """ dispatch order """
        self.setDateDispatched(DateTime())
        self.reindexObject()

    security.declareProtected(View, 'getProductUIDs')
    def getProductUIDs(self):
        """ return the uids of the products referenced by order items
        """
        uids = []
        for orderitem in self.objectValues('OrderItem'):
            product = orderitem.getProduct()
            if product is not None:
                uids.append(orderitem.getProduct().UID())
        return uids

    security.declarePublic('current_date')
    def current_date(self):
        """ return current date """
        return DateTime()



atapi.registerType(Order, PROJECTNAME)
