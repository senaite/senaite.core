from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore import permissions
from Products.bika.ClientStatus import schema as status_schema
from Products.bika.tools import ToolFolder
from Products.bika.utils import make_listing_from_schema
from Products.bika.interfaces.tools import Ibika_client_status
from five import grok

columns = ('title',)
status_listing = make_listing_from_schema(status_schema, columns)

class bika_client_status(ToolFolder):
    """ Container for client status"""

    grok.implements(Ibika_client_status)

    security = ClassSecurityInfo()
    id = 'bika_client_status'
    title = 'Client status'
    description = ''
    meta_type = 'Bika Client Status Tool'
    managed_portal_type = 'ClientStatus'
    listing_schema = status_listing 

InitializeClass(bika_client_status)
