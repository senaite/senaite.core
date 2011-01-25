from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore import permissions
from Products.bika.LabARProfile import schema as labprofiles_schema
from Products.bika.tools import ToolFolder
from Products.bika.utils import make_listing_from_schema
from Products.bika.interfaces.tools import Ibika_arprofiles
from five import grok

columns = ('title', 'ProfileKey')
labprofiles_listing = make_listing_from_schema(labprofiles_schema, columns)

class bika_arprofiles(ToolFolder):
    """ Container for lab analysis profiles """

    grok.implements(Ibika_arprofiles)

    security = ClassSecurityInfo()
    id = 'bika_arprofiles'
    title = 'Lab analysis profiles'
    description = 'Setup the analysis request profiles.'
    meta_type = 'Bika Analysis Profiles Tool'
    managed_portal_type = 'LabARProfile'
    listing_schema = labprofiles_listing 

InitializeClass(bika_arprofiles)
