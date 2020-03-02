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

from bika.lims import api
from bika.lims import logger
from plone.memoize.ram import cache
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import implements


class IBootstrapView(Interface):
    """Twitter Bootstrap View
    """

    def getColumnsClasses(view=None):
        """A helper method to return the clases for the columns of the site
           it should return a dict with three elements:'one', 'two', 'content'
           Each of them should contain the classnames for the first (leftmost)
           second (rightmost) and middle column
        """

    def getViewportValues(view=None):
        """Determine the value of the viewport meta-tag
        """


def icon_cache_key(method, self, brain_or_object):
    """Generates a cache key for the icon lookup

    Includes the virtual URL to handle multiple HTTP/HTTPS domains
    Example: http://senaite.local/clients?modified=1512033263370
    """
    url = api.get_url(brain_or_object)
    modified = api.get_modification_date(brain_or_object).millis()
    key = "{}?modified={}".format(url, modified)
    logger.debug("Generated Cache Key: {}".format(key))
    return key


class BootstrapView(BrowserView):
    """Twitter Bootstrap helper view for SENAITE LIMS
    """
    implements(IBootstrapView)

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)

    @cache(icon_cache_key)
    def get_icon_for(self, brain_or_object):
        """Get the navigation portlet icon for the brain or object

        The cache key ensures that the lookup is done only once per domain name
        """
        portal_types = api.get_tool("portal_types")
        fti = portal_types.getTypeInfo(api.get_portal_type(brain_or_object))
        icon = fti.getIcon()
        if not icon:
            return ""
        # Always try to get the big icon for high-res displays
        icon_big = icon.replace(".png", "_big.png")
        # fall back to a default icon if the looked up icon does not exist
        if self.context.restrictedTraverse(icon_big, None) is None:
            icon_big = None
        portal_url = api.get_url(api.get_portal())
        title = api.get_title(brain_or_object)
        html_tag = "<img title='{}' src='{}/{}' width='16' />".format(
            title, portal_url, icon_big or icon)
        logger.debug("Generated Icon Tag for {}: {}".format(
            api.get_path(brain_or_object), html_tag))
        return html_tag

    def getViewportValues(self, view=None):
        """Determine the value of the viewport meta-tag
        """
        values = {
            'width': 'device-width',
            'initial-scale': '1.0',
        }

        return ','.join('%s=%s' % (k, v) for k, v in values.items())

    def getColumnsClasses(self, view=None):
        """Determine whether a column should be shown. The left column is
           called plone.leftcolumn; the right column is called
           plone.rightcolumn.
        """

        plone_view = getMultiAdapter(
            (self.context, self.request), name=u'plone')
        portal_state = getMultiAdapter(
            (self.context, self.request), name=u'plone_portal_state')

        sl = plone_view.have_portlets('plone.leftcolumn', view=view)
        sr = plone_view.have_portlets('plone.rightcolumn', view=view)

        isRTL = portal_state.is_rtl()

        # pre-fill dictionary
        columns = dict(one="", content="", two="")

        if not sl and not sr:
            # we don't have columns, thus conten takes the whole width
            columns['content'] = "col-md-12"

        elif sl and sr:
            # In case we have both columns, content takes 50% of the whole
            # width and the rest 50% is spread between the columns
            columns['one'] = "col-xs-12 col-md-2"
            columns['content'] = "col-xs-12 col-md-8"
            columns['two'] = "col-xs-12 col-md-2"

        elif (sr and not sl) and not isRTL:
            # We have right column and we are NOT in RTL language
            columns['content'] = "col-xs-12 col-md-10"
            columns['two'] = "col-xs-12 col-md-2"

        elif (sl and not sr) and isRTL:
            # We have left column and we are in RTL language
            columns['one'] = "col-xs-12 col-md-2"
            columns['content'] = "col-xs-12 col-md-10"

        elif (sl and not sr) and not isRTL:
            # We have left column and we are in NOT RTL language
            columns['one'] = "col-xs-12 col-md-2"
            columns['content'] = "col-xs-12 col-md-10"

        # # append cell to each css-string
        # for key, value in columns.items():
        #     columns[key] = "cell " + value

        return columns
