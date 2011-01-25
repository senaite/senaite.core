from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore import permissions
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.bika.tools import ToolFolder
from Products.bika.interfaces.tools import Ibika_portal_ids
from five import grok
import os
import sys
import urllib


class IDServerUnavailable(Exception):
    pass

class bika_portal_ids(UniqueObject, SimpleItem):
    """ Portal ID Tool """

    grok.implements(Ibika_portal_ids)

    security = ClassSecurityInfo()
    id = 'bika_portal_ids'
    title = 'Portal Ids'
    description = 'Generates IDs for objects'
    meta_type = 'Portal ID Tool'
    listing_schema = None 
    default_template = 'tool_settings_view'

    security.declareProtected(permissions.View, 'generate_id')
    def generate_id(self, portal_type, batch_size = None):
        """ Generate a new id for 'portal_type'
        """
        if portal_type == 'News Item':
            portal_type = 'NewsItem'
        idserver_url = os.environ.get('IDServerURL')
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal_id = portal.getId()
        try:
            if batch_size:
                # GET
                f = urllib.urlopen('%s/%s%s?%s' % (
                        idserver_url,
                        portal_id,
                        portal_type,
                        urllib.urlencode({'batch_size': batch_size}))
                        )
            else:
                f = urllib.urlopen('%s/%s%s' % (
                    idserver_url, portal_id, portal_type
                    )
                )
            id = f.read()
            f.close()
        except:
            from sys import exc_info
            info = exc_info()
            import zLOG; zLOG.LOG('INFO', 0, '', 'generate_id raised exception: %s, %s \n idserver_url: %s' % (info[0], info[1], idserver_url))
            raise IDServerUnavailable('ID Server unavailable')
        return id

InitializeClass(bika_portal_ids)
