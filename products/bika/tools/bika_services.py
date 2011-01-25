from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.bika.tools import ToolFolder
from Products.bika.interfaces.tools import Ibika_services
from five import grok

class bika_services(ToolFolder):
    """ Container for analysis services """

    grok.implements(Ibika_services)

    security = ClassSecurityInfo()
    id = 'bika_services'
    title = 'Analysis services'
    description = 'Setup the services we offer our clients.'
    meta_type = 'Bika Services Tool'
    managed_portal_type = 'AnalysisService'
    listing_schema = None 
    default_template = 'analysisservices' 

InitializeClass(bika_services)
