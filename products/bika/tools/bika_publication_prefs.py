from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore import permissions
from Products.bika.ClientPublicationPreference import schema as pubpref_schema
from Products.bika.tools import ToolFolder
from Products.bika.utils import make_listing_from_schema
from Products.bika.interfaces.tools import Ibika_publication_prefs
from five import grok

columns = ('title',)
pubpref_listing = make_listing_from_schema(pubpref_schema, columns)

class bika_publication_prefs(ToolFolder):
    """ Container for client publication preferences """

    grok.implements(Ibika_publication_prefs)

    security = ClassSecurityInfo()
    id = 'bika_publication_prefs'
    title = 'Publication preferences'
    description = ''
    meta_type = 'Bika Publication Preferences Tool'
    managed_portal_type = 'ClientPublicationPreference'
    listing_schema = pubpref_listing 

InitializeClass(bika_publication_prefs)
