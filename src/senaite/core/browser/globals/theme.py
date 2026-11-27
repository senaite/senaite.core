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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import os
import time
from email.utils import formatdate
from email.utils import mktime_tz
from email.utils import parsedate_tz
from mimetypes import guess_type
from string import Template

from bika.lims import api
from bika.lims.utils import render_html_attributes
from plone.memoize.ram import cache
from plone.memoize.view import memoize
from plone.resource.interfaces import IResourceDirectory
from Products.Five.browser import BrowserView
from senaite.core import logger
from zExceptions import NotFound
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import subscribers
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.traversing.interfaces import ITraversable
from zope.traversing.interfaces import TraversalError

from .interfaces import IIconProvider
from .interfaces import ISenaiteTheme

IMG_TAG = Template("""<img src="$src" $attr />""")

ICON_BASE_URL = "++plone++senaite.core.static/assets/icons"

# Icon that is returned when no icon is found for a name
ICON_NOT_FOUND = "icon-not-found"

# Seconds a browser may cache an icon
ICON_MAX_AGE = 86400

# Theme functions that can be traversed to in page templates
THEME_FUNCTIONS = ISenaiteTheme.names()

# Theme functions that can be called by URL with an icon name
ICON_FUNCTIONS = ("icon", "icon_data", "icon_path", "icon_url", "icon_tag")


def icon_cache_key(method, instance):
    return time.time() // 86400  # 1 day


@implementer(ITraversable)
class Traverser(object):

    def __init__(self, func):
        self.func = func

    def traverse(self, name, furtherPath):
        if furtherPath:
            raise TraversalError("Do not know how to handle further path")
        return self.func(name)


@implementer(ISenaiteTheme, ITraversable, IPublishTraverse)
class SenaiteTheme(BrowserView):
    """Theme specific configuration view

    The purpose of this view is to deliver assets, e.g. icons or other
    configuration entries, for page templates, view classes or JavaScripts,
    so that these can be easily overridden.

    For exmple, to render an icon in a page page, we can do now this:

    ```
    <img i18n:attributes="title" title="Sample" src="#"
         tal:attributes="src senaite_theme/icon_url/sample" />
    ```

    Note: The `senaite_theme` view is hooked into the `main_template.pt`,
          so that it is globally available in all page templates.

    When the icon shall be included via a browser view, the icon url needs to
    provide the icon directly:

    ```
    def __call__(self):
         senaite_theme = self.context.restrictedTraverse("@@senaite_theme")
         self.icon = senaite_theme.icon("plus")

    <img tal:attributes="src view/icon"/>
    ```

    The same must be done in JavaScripts (here a coffee-script):

    ```
    add_btn_src = "#{window.portal_url}/senaite_theme/icon/plus"
    add_btn = $("<img class='addbtn' src='#{add_btn_src}' />")
    ```

    Furthermore, the resources can be fetched by URL.

        - Get the relative icon URL:
        http://localhost:8080/senaite/senaite_theme/icon_path/sample

        - Get the absolute icon URL:
        http://localhost:8080/senaite/senaite_theme/icon_url/sample

        - Get the icon tag with additional HTML attributes
        http://localhost:8080/senaite/senaite_theme/icon_tag/sample?width=16&class=icon
    """

    def __init__(self, context, request):
        super(SenaiteTheme, self).__init__(context, request)
        self.traverse_subpath = []

    @cache(icon_cache_key)
    def icons(self):
        """Returns a mapping of icons -> icon path
        """
        icons = {}
        static_dir = getUtility(
            IResourceDirectory, name=u"++plone++senaite.core.static")
        icon_dir = static_dir["assets"]["icons"]
        for icon in icon_dir.listDirectory():
            name, ext = os.path.splitext(icon)
            icons[name] = "{}/{}".format(ICON_BASE_URL, icon)
            icons[icon] = "{}/{}".format(ICON_BASE_URL, icon)
        # call icon providers
        adapters = subscribers((self, self.context), IIconProvider)
        for adapter in sorted(
                adapters, key=lambda a: api.to_float(
                    getattr(a, "priority_order", 1000))):
            icons.update(adapter.icons())
        logger.info("+++ Found {} icons +++".format(len(icons)))
        return icons

    def get_theme_function(self, name, allowed=THEME_FUNCTIONS):
        """Returns the theme function of the given name or None
        """
        if name not in allowed:
            return None
        return getattr(self, name, None)

    def traverse(self, name, furtherPath):
        func = self.get_theme_function(name)
        if func is None:
            raise TraversalError(name)
        if furtherPath:
            return Traverser(func)
        return func

    def publishTraverse(self, request, name):
        """Called before __call__ for each path name and allows to dispatch
        subpaths to methods
        """
        self.traverse_subpath.append(name)
        return self

    def handle_subpath(self):
        """Call the theme function with the icon name of the subpath
        """
        name = self.traverse_subpath[0]
        func = self.get_theme_function(name, allowed=ICON_FUNCTIONS)
        # The icon name is the only path segment after the function name
        args = self.traverse_subpath[1:]
        if func is None or len(args) != 1:
            raise NotFound(name)
        kwargs = self.request.form
        return func(*args, **kwargs)

    def __call__(self):
        if len(self.traverse_subpath) > 0:
            return self.handle_subpath()
        raise NotFound(self.__name__)

    @property
    @memoize
    def portal_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="plone_portal_state")

    @memoize
    def portal(self):
        return self.portal_state.portal()

    @memoize
    def portal_url(self):
        return self.portal_state.portal_url()

    def get_icon_file(self, name, **kw):
        """Returns the file system path of the named icon
        """
        icon = self.icon_path(name, **kw)
        resource = self.context.restrictedTraverse(icon)
        return resource.path

    def read_file(self, path):
        """Returns the data of the file
        """
        with open(path, "rb") as f:
            return f.read()

    def is_modified_since(self, last_modified):
        """Checks if the browser has an older version than the given time
        """
        header = self.request.getHeader("If-Modified-Since")
        if not header:
            return True
        since = parsedate_tz(header)
        if since is None:
            return True
        return int(last_modified) > mktime_tz(since)

    def icon_data(self, name, **kw):
        """Return the raw filedata of the icon
        """
        path = self.get_icon_file(name, **kw)
        return self.read_file(path)

    def icon(self, name, **kw):
        """Returns the icon as response that the browser may cache
        """
        path = self.get_icon_file(name, **kw)
        last_modified = os.path.getmtime(path)
        response = self.request.response
        response.setHeader("Last-Modified",
                           formatdate(last_modified, usegmt=True))
        response.setHeader("Cache-Control",
                           "public, max-age={}".format(ICON_MAX_AGE))
        if not self.is_modified_since(last_modified):
            response.setStatus(304)
            return ""
        response.setHeader("Content-Type", guess_type(path)[0])
        return self.read_file(path)

    @memoize
    def icon_path(self, name, **kw):
        """Returns the relative url for the named icon

        :param name: named icon from the theme config
        :returns: absolute image URL
        """
        icons = self.icons()
        default = kw.get("default", ICON_NOT_FOUND)
        return icons.get(name) or icons.get(default) or icons[ICON_NOT_FOUND]

    @memoize
    def icon_url(self, name, **kw):
        """Returns the absolute url for the named icon

        :param name: name of the icon
        :returns: absolute image URL
        """
        portal_url = self.portal_url()
        icon_path = self.icon_path(name, **kw)
        return "{}/{}".format(portal_url, icon_path)

    @memoize
    def icon_tag(self, name, **kw):
        """Returns a generated <img/> tag for the named icon

        :param name: name of the icon
        :returns: HTML <img/> tag
        """
        default = kw.pop("default", ICON_NOT_FOUND)
        url = self.icon_url(name, default=default)
        attr = render_html_attributes(**kw)
        tag = IMG_TAG.safe_substitute(src=url, attr=attr)
        return tag

    def __bobo_traverse__(self, REQUEST, name):
        """Helper to access icons the old way during `unrestrictedTraverse` calls
        """
        if isinstance(REQUEST, dict):
            return self.publishTraverse(REQUEST, name)
        return self
