from zope.app.component.hooks import getSite
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IIdServer
from zope.interface.declarations import implements
import os
import sys
import urllib

class IDServerUnavailable(Exception):
    pass

class bika_idserver(object):

    implements(IIdServer)
    security = ClassSecurityInfo()


    security.declarePublic('generate_id')
    def generate_id(self, portal_type, batch_size = None):
        """ Generate a new id for 'portal_type'
        """
        if portal_type == 'News Item':
            portal_type = 'NewsItem'
        idserver_url = os.environ.get('IDServerURL')

        plone = getSite()
        portal_id = plone.getId()
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
            raise IDServerUnavailable(_('ID Server unavailable'))
        return id
