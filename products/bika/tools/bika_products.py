from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore import permissions
from Products.bika.LabProduct import schema as product_schema
from Products.bika.tools import ToolFolder
from Products.bika.utils import make_listing_from_schema
from Products.bika.interfaces.tools import Ibika_products
from five import grok

columns = ('title', 'Volume', 'Unit', 'Price', 'VATAmount', 'TotalPrice')
product_listing = make_listing_from_schema(product_schema, columns)

class bika_products(ToolFolder):
    """ Container for lab products """

    grok.implements(Ibika_products)

    security = ClassSecurityInfo()
    id = 'bika_products'
    title = 'Lab products'
    description = 'Setup the products sold to our clients.'
    meta_type = 'Bika Products Tool'
    managed_portal_type = 'LabProduct'
    listing_schema = product_listing 

InitializeClass(bika_products)
