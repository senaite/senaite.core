from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore import permissions
from Products.bika.Method import schema as method_schema
from Products.bika.tools import ToolFolder
from Products.bika.utils import make_listing_from_schema
from Products.bika.interfaces.tools import Ibika_methods
from five import grok

columns = ('title')
method_listing = make_listing_from_schema(method_schema, columns)

class bika_methods(ToolFolder):
    """ Container for lab methods """

    grok.implements(Ibika_methods)

    security = ClassSecurityInfo()
    id = 'bika_methods'
    title = 'Lab methods'
    description = 'Setup the methods used in the lab.'
    meta_type = 'Bika Methods Tool'
    managed_portal_type = 'Method'
    listing_schema = method_listing 

InitializeClass(bika_methods)
