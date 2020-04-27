# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.interfaces import IIdServer
from zope.interface.declarations import implements
from hashlib import sha1
import App,os,sys,random,time,urllib,hmac

try:
    from zope.component.hooks import getSite
except:
    # Plone < 4.3
    from zope.app.component.hooks import getSite

class IDServerUnavailable(Exception):
    pass

class bika_idserver(object):

    implements(IIdServer)
    security = ClassSecurityInfo()

    security.declarePublic('generate_id')
    def generate_id(self, portal_type, batch_size = None):
        """ Generate a new id for 'portal_type'
        """
        plone = getSite()
        portal_id = plone.getId()

        if portal_type == 'News Item':
            portal_type = 'NewsItem'

        idserver_url = os.environ.get('IDServerURL')
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
