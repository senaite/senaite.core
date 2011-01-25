from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore import permissions
from Products.bika.StandardManufacturer import schema as standardmanufacturer_schema
from Products.bika.tools import ToolFolder
from Products.bika.utils import make_listing_from_schema
from Products.bika.interfaces.tools import Ibika_standardmanufacturers
from five import grok

columns = ('title', 'StandardManufacturerDescription')
standardmanufacturer_listing = make_listing_from_schema(standardmanufacturer_schema, columns)

class bika_standardmanufacturers(ToolFolder):
    """ Container for standard manufacturers """

    grok.implements(Ibika_standardmanufacturers)

    security = ClassSecurityInfo()
    id = 'bika_standardmanufacturers'
    title = 'Standard Manufacturers'
    description = ''
    meta_type = 'Bika Standard Manufacturers Tool'
    managed_portal_type = 'StandardManufacturer'
    listing_schema = standardmanufacturer_listing 

InitializeClass(bika_standardmanufacturers)

