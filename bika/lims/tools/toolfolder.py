from AccessControl import ClassSecurityInfo
from Acquisition import ImplicitAcquisitionWrapper as iaw
from App.class_init import InitializeClass
from OFS.Folder import Folder
from Products.Archetypes.public import BaseSchema
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject, getToolByName
from bika.lims.interfaces.tools import IToolFolder
from zope.interface import implements

class ToolFolder(UniqueObject, Folder):
    """ Tool Folder """

    implements(IToolFolder)

    security = ClassSecurityInfo()
    id = 'tool_folder'
    managed_portal_type = ''
    listing_schema = BaseSchema
    default_template = 'tool_contents'

    def index_html(self, REQUEST, RESPONSE):
        """ return tool_contents template """
        template = getattr(self, self.default_template)
        return template(REQUEST = RESPONSE, RESPONSE = REQUEST)

    security.declareProtected(permissions.AddPortalContent, 'invokeFactory')
    def invokeFactory(self, type_name, id, RESPONSE = None, *args, **kw):
        '''Invokes the portal_types tool.
           XXX is it here that objects are created too soon (without invoking their factories perhaps)?'''
        pt = getToolByName(self, 'portal_types')
        myType = pt.getTypeInfo(self)
        args = (type_name, self, id, RESPONSE) + args
        new_id = pt.constructContent(*args, **kw)
        if new_id is None or new_id == '':
            new_id = id
        return new_id

    security.declarePublic('getListingSchema')
    def getListingSchema(self):
        """ return listed fields """
        schema = iaw(self.listing_schema, self)
        return schema

InitializeClass(ToolFolder)
