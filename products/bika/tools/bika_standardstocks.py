from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.bika.tools import ToolFolder
from Products.bika.interfaces.tools import Ibika_standardstocks
from five import grok

class bika_standardstocks(ToolFolder):
    """ Container for standard stocks """

    grok.implements(Ibika_standardstocks)

    security = ClassSecurityInfo()
    id = 'bika_standardstocks'
    title = 'Standard Stocks'
    description = ''
    meta_type = 'Bika Standard Stocks Tool'
    managed_portal_type = 'StandardStock'
    listing_schema = None 
    default_template = 'standardstocks' 

InitializeClass(bika_standardstocks)
