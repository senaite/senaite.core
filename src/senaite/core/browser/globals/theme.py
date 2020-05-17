# -*- coding: utf-8 -*-

import json
import os
from string import Template
from mimetypes import guess_type

from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from plone.resource.interfaces import IResourceDirectory
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.traversing.interfaces import ITraversable
from zope.traversing.interfaces import TraversalError

from .interfaces import ISenaiteTheme

IMG_TAG = Template("""<img src="$src" $attr />""")
ICON_BASE_URL = "++plone++senaite.core.static/assets/svg"


@implementer(ITraversable)
class Traverser(object):

    def __init__(self, func):
        self.func = func

    def traverse(self, name, furtherPath):
        if furtherPath:
            raise TraversalError("Do not know how to handle further path")
        else:
            if self.func:
                return self.func(name)
            else:
                raise TraversalError(name)


@implementer(ISenaiteTheme, ITraversable, IPublishTraverse)
class SenaiteTheme(BrowserView):
    """Information about the state of the current context
    """

    def __init__(self, context, request):
        super(SenaiteTheme, self).__init__(context, request)
        self.traverse_subpath = []

    @property
    @memoize_contextless
    def icons(self):
        """Returns a mapping of icons -> icon path
        """
        icons = {}
        static_dir = getUtility(
            IResourceDirectory, name=u"++plone++senaite.core.static")
        icon_dir = static_dir["assets"]["svg"]
        for icon in icon_dir.listDirectory():
            name, ext = os.path.splitext(icon)
            icons[name] = "{}/{}".format(ICON_BASE_URL, icon)
            icons[icon] = "{}/{}".format(ICON_BASE_URL, icon)
        return icons

    def traverse(self, name, furtherPath):
        attr = getattr(self, name, None)
        if attr is None:
            raise TraversalError(name)
        if callable(attr) and furtherPath:
            return Traverser(attr)
        return attr

    def publishTraverse(self, request, name):
        """Called before __call__ for each path name and allows to dispatch
        subpaths to methods
        """
        self.traverse_subpath.append(name)
        return self

    def handle_subpath(self, prefix=""):
        # check if the method exists
        func_arg = self.traverse_subpath[0]
        func_name = "{}{}".format(prefix, func_arg)
        func = getattr(self, func_name, None)
        if func is None:
            raise NameError("Invalid function name")
        # Additional provided path segments after the function name are handled
        # as positional arguments
        args = self.traverse_subpath[1:]
        kwargs = self.request.form
        return func(*args, **kwargs)
        return json.dumps(func(*args, **kwargs))

    def __call__(self):
        if len(self.traverse_subpath) > 0:
            return self.handle_subpath()
        return super(SenaiteTheme, self).__call__()

    @property
    @memoize
    def portal_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="plone_portal_state")

    @memoize_contextless
    def portal(self):
        return self.portal_state.portal()

    @memoize_contextless
    def portal_url(self):
        return self.portal_state.portal_url()

    @memoize_contextless
    def icon(self, name, **kw):
        icon = self.icon_path(name, **kw)
        response = self.request.response
        resource = self.context.restrictedTraverse(icon)
        mimetype = guess_type(icon)[0]
        with open(resource.path, "rb") as f:
            response.setHeader("content-type", mimetype)
            return self.request.response.write(f.read())

    @memoize_contextless
    def icon_path(self, name, **kw):
        """Returns the relative url for the named icon

        :param name: named icon from the theme config
        :returns: absolute image URL
        """
        icons = self.icons
        default = kw.get("default", "icon-not-found")
        return icons.get(name, icons.get(default))

    @memoize_contextless
    def icon_url(self, name, **kw):
        """Returns the absolute url for the named icon

        :param name: name of the icon
        :returns: absolute image URL
        """
        portal_url = self.portal_url()
        icon_path = self.icon_path(name)
        return "{}/{}".format(portal_url, icon_path)

    @memoize_contextless
    def icon_tag(self, name, **kw):
        """Returns a generated <img/> tag for the named icon

        :param name: name of the icon
        :returns: HTML <img/> tag
        """
        url = self.icon_url(name)
        attr = list()
        if kw:
            attr = ['{}="{}"'.format(k, v) for k, v in kw.items()]
        attr = " ".join(attr).replace("css_class", "class")
        tag = IMG_TAG.safe_substitute(src=url, attr=attr)
        return tag
