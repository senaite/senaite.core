from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore import permissions
from Products.bika.ClientCategory import schema as category_schema
from Products.bika.tools import ToolFolder
from Products.bika.utils import make_listing_from_schema
from Products.bika.interfaces.tools import Ibika_client_categories
from five import grok

columns = ('title',)
category_listing = make_listing_from_schema(category_schema, columns)

class bika_client_categories(ToolFolder):
    """ Container for client categories """

    grok.implements(Ibika_client_categories)

    security = ClassSecurityInfo()
    id = 'bika_client_categories'
    title = 'Client categories'
    description = ''
    meta_type = 'Bika Client Categories Tool'
    managed_portal_type = 'ClientCategory'
    listing_schema = category_listing 

InitializeClass(bika_client_categories)
