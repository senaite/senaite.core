from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.bika.tools import ToolFolder
from Products.bika.interfaces.tools import Ibika_labinfo
from five import grok

class bika_labinfo(ToolFolder):
    """ Container for laboratory """

    grok.implements(Ibika_labinfo)

    security = ClassSecurityInfo()
    id = 'bika_labinfo'
    title = 'Laboratory information'
    description = 'Laboratory information includes the name of the laboratory, contact numbers, physical and postal address, email address and the laboratory personnel and their contact details'
    meta_type = 'Bika Laboratory Information Tool'
    managed_portal_type = 'Laboratory'
    listing_schema = None 
    default_template = 'bika_labinfo_view'
    # XXX: Temporary workaround to enable importing of exported bika
    # instance. If '__replaceable__' is not set we get BadRequest, The
    # id is invalid - it is already in use.
    
    __replaceable__ = 1

    # XXX Some how the dependancies between genericsetup importSteps don't take,
    # so this object needs to be created in setuphandlers, otherwise the tool
    # tries to create the object before the content type is defined.
    #
    #def manage_afterAdd(self, item, container):
    #    """ Add laboratory """
    #    self.invokeFactory(id = 'laboratory', type_name = 'Laboratory')


InitializeClass(bika_labinfo)
