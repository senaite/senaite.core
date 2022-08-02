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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.


from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import logger
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView as BaseBrowserView
from senaite.core.api.dtime import to_localized_time as ulocalized_time
from zope.cachedescriptors.property import Lazy as lazy_property
from zope.i18n import translate


class BrowserView(BaseBrowserView):
    security = ClassSecurityInfo()

    logger = logger

    def __init__(self, context, request):
        self.context = context
        self.request = request
        super(BrowserView, self).__init__(context, request)

    security.declarePublic('ulocalized_time')

    def ulocalized_time(self, time, long_format=None, time_only=None):
        return ulocalized_time(time, long_format, time_only,
                               context=self.context, request=self.request)

    @lazy_property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    @lazy_property
    def portal_url(self):
        return self.portal.absolute_url().split("?")[0]

    @lazy_property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @lazy_property
    def reference_catalog(self):
        return getToolByName(self.context, 'reference_catalog')

    @lazy_property
    def senaite_catalog_analysis(self):
        return getToolByName(self.context, 'senaite_catalog_analysis')

    @lazy_property
    def senaite_catalog_setup(self):
        return getToolByName(self.context, 'senaite_catalog_setup')

    @lazy_property
    def senaite_catalog(self):
        return getToolByName(self.context, 'senaite_catalog')

    @lazy_property
    def portal_membership(self):
        return getToolByName(self.context, 'portal_membership')

    @lazy_property
    def portal_groups(self):
        return getToolByName(self.context, 'portal_groups')

    @lazy_property
    def portal_workflow(self):
        return getToolByName(self.context, 'portal_workflow')

    @lazy_property
    def checkPermission(self, perm, obj):
        return self.portal_membership.checkPermission(perm, obj)

    # TODO: user_fullname is deprecated and will be removed in Bika LIMS 3.3.
    # Use bika.utils.user_fullnameinstead
    # I was having a problem trying to import the function from bika.lims.utils
    # so i copied the code here.
    def user_fullname(self, userid):
        member = self.portal_membership.getMemberById(userid)
        if member is None:
            return userid
        member_fullname = member.getProperty('fullname')
        portal_catalog = getToolByName(self, 'portal_catalog')
        c = portal_catalog(portal_type='Contact', getUsername=userid)
        contact_fullname = c[0].getObject().getFullname() if c else None
        return contact_fullname or member_fullname or userid

    # TODO: user_fullname is deprecated and will be removed in Bika LIMS 3.3.
    # Use bika.utils.user_fullnameinstead.
    # I was having a problem trying to import the function from bika.lims.utils
    # so i copied the code here.
    def user_email(self, userid):
        member = self.portal_membership.getMemberById(userid)
        if member is None:
            return userid
        member_email = member.getProperty('email')
        portal_catalog = getToolByName(self, 'portal_catalog')
        c = portal_catalog(portal_type='Contact', getUsername=userid)
        contact_email = c[0].getObject().getEmailAddress() if c else None
        return contact_email or member_email or ''

    def python_date_format(self, long_format=None, time_only=False):
        """This convert bika domain date format msgstrs to Python
        strftime format strings, by the same rules as ulocalized_time.
        XXX i18nl10n.py may change, and that is where this code is taken from.
        """
        # get msgid
        msgid = long_format and 'date_format_long' or 'date_format_short'
        if time_only:
            msgid = 'time_format'
        # get the formatstring
        formatstring = translate(msgid, domain="senaite.core",
                                 context=self.request)

        if formatstring is None or formatstring.startswith(
                'date_') or formatstring.startswith('time_'):
            self.logger.error("bika/%s/%s could not be translated" %
                              (self.request.get('LANGUAGE'), msgid))
            # msg catalog was not able to translate this msgids
            # use default setting
            if long_format:
                key = "Products.CMFPlone.i18nl10n.override_dateformat.date_format_long"
                format = api.get_registry_record(key)
            else:
                key = "Products.CMFPlone.i18nl10n.override_dateformat.time_format"
                format = api.get_registry_record(key)
            return format
        return formatstring.replace(r"${", '%').replace('}', '')

    @lazy_property
    def date_format_long(self):
        fmt = self.python_date_format(long_format=1)
        if fmt == "date_format_long":
            fmt = "%Y-%m-%d %I:%M %p"
        return fmt

    @lazy_property
    def date_format_short(self):
        fmt = self.python_date_format()
        if fmt == "date_format_short":
            fmt = "%Y-%m-%d"
        return fmt

    @lazy_property
    def time_format(self):
        fmt = self.python_date_format(time_only=True)
        if fmt == "time_format":
            fmt = "%I:%M %p"
        return fmt
