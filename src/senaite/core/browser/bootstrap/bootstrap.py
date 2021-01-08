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

import os

from bika.lims import api
from plone.memoize.ram import cache
from plone.memoize.view import memoize
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import implementer

SVG_ICON_BASE_URL = "++plone++senaite.core.static/assets/icons"


class IBootstrapView(Interface):
    """Twitter Bootstrap View
    """

    def get_columns_classes(view=None):
        """A helper method to return the clases for the columns of the site
           it should return a dict with three elements:'one', 'two', 'content'
           Each of them should contain the classnames for the first (leftmost)
           second (rightmost) and middle column
        """

    def get_viewport_values(view=None):
        """Determine the value of the viewport meta-tag
        """

    def get_data_settings():
        """Helper method to inject data attributes in a DOM node
        """


def icon_cache_key(method, self, brain_or_object, **kw):
    """Generates a cache key for the icon lookup

    Includes the virtual URL to handle multiple HTTP/HTTPS domains
    Example: http://senaite.local/clients?modified=1512033263370
    """
    url = api.get_url(brain_or_object)
    modified = api.get_modification_date(brain_or_object).millis()
    attrs = "&".join(map(lambda a: "{}={}".format(*a), kw.items()))
    key = "{}?modified={}{}".format(url, modified, attrs)
    return key


@implementer(IBootstrapView)
class BootstrapView(BrowserView):
    """Twitter Bootstrap helper view for SENAITE LIMS
    """

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)

    @property
    @memoize
    def senaite_theme(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="senaite_theme")

    @property
    @memoize
    def portal_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name=u"plone_portal_state")

    @property
    @memoize
    def context_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="plone_context_state")

    def resource_exists(self, resource):
        """Checks if a resouce exists
        """
        return self.context.restrictedTraverse(resource, None) is not None

    def img_tag(self, title=None, icon=None, **kw):
        """Generate an img tag
        """
        attributes = kw
        if not kw:
            attributes = {"width": "16"}
        css = attributes.pop("css_class", "")
        attributes["class"] = css
        attributes.update(kw)
        attrs = " ".join(
            map(lambda a: "{}='{}'".format(a[0], a[1]), attributes.items()))
        portal_url = api.get_url(api.get_portal())
        html_tag = "<img title='{}' src='{}/{}' {} />".format(
            title, portal_url, icon, attrs)
        return html_tag

    @cache(icon_cache_key)
    def get_icon_for(self, brain_or_object, **kw):
        """Get the navigation portlet icon for the brain or object

        The cache key ensures that the lookup is done only once per domain name
        """
        portal_types = api.get_tool("portal_types")
        fti = portal_types.getTypeInfo(api.get_portal_type(brain_or_object))
        icon = fti and fti.getIcon()  # handle non-type fti for bbb
        if not icon:
            return ""
        title = api.get_title(brain_or_object)
        # Always try to get the SVG icon for high-res displays
        icon_basename = os.path.basename(icon)
        # XXX use senaite_theme view to fetch the icon from the icons() dict
        svg = icon_basename.replace(".png", ".svg")

        icon_big = icon.replace(".png", "_big.png")
        icon_svg = "{}/{}".format(SVG_ICON_BASE_URL, svg)

        if self.resource_exists(icon_svg):
            return self.img_tag(title=title, icon=icon_svg, **kw)
        # or try to get the big icon for high-res displays
        elif self.resource_exists(icon_big):
            return self.img_tag(title=title, icon=icon_big, **kw)
        return self.img_tag(title=title, icon=icon, **kw)

    def get_data_settings(self):
        """Returns data attributes for a DOM node
        """
        # do not use getSite because it's possible it could be different
        # than the actual portal url
        portal_url = self.portal_state.portal_url()
        setup = api.get_setup()
        data = {
            "data-base-url": self.context.absolute_url(),
            "data-view-url": self.context_state.view_url(),
            "data-portal-url": portal_url,
            "data-i18ncatalogurl": portal_url + "/plonejsi18n",
            "data-auto-logoff": setup.getAutoLogOff(),
        }
        return data

    def get_viewport_values(self, view=None):
        """Determine the value of the viewport meta-tag
        """
        values = {
            "width": "device-width",
            "initial-scale": "0.8",
        }

        return ",".join("%s=%s" % (k, v) for k, v in values.items())

    def get_columns_classes(self, view=None):
        """Determine whether a column should be shown. The left column is
           called plone.leftcolumn; the right column is called
           plone.rightcolumn.
        """

        layout = getMultiAdapter(
            (self.context, self.request), name=u"plone_layout")
        state = getMultiAdapter(
            (self.context, self.request), name=u"plone_portal_state")

        sl = layout.have_portlets("plone.leftcolumn", view=view)
        sr = layout.have_portlets("plone.rightcolumn", view=view)

        isRTL = state.is_rtl()

        # pre-fill dictionary
        columns = dict(one="", content="", two="")

        if not sl and not sr:
            # we don"t have columns, thus conten takes the whole width
            columns["content"] = "col-md-12"

        elif sl and sr:
            # In case we have both columns, content takes 50% of the whole
            # width and the rest 50% is spread between the columns
            columns["one"] = "col-xs-12 col-md-2"
            columns["content"] = "col-xs-12 col-md-8"
            columns["two"] = "col-xs-12 col-md-2"

        elif (sr and not sl) and not isRTL:
            # We have right column and we are NOT in RTL language
            columns["content"] = "col-xs-12 col-md-10"
            columns["two"] = "col-xs-12 col-md-2"

        elif (sl and not sr) and isRTL:
            # We have left column and we are in RTL language
            columns["one"] = "col-xs-12 col-md-2"
            columns["content"] = "col-xs-12 col-md-10"

        elif (sl and not sr) and not isRTL:
            # We have left column and we are in NOT RTL language
            columns["one"] = "col-xs-12 col-md-2"
            columns["content"] = "col-xs-12 col-md-10"

        return columns
