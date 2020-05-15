# -*- coding: utf-8 -*-

from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from Products.Five.browser import BrowserView
from senaite.core.config import theme
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

from .interfaces import ISenaiteTheme


@implementer(ISenaiteTheme, IPublishTraverse)
class SenaiteTheme(BrowserView):
    """Information about the state of the current context
    """

    def __init__(self, context, request):
        super(SenaiteTheme, self).__init__(context, request)
        self.traverse_subpath = []
        # Allow path traversal in page templates
        self.config = self.theme_config()
        self.icons = self.config.get("icons", {})

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
        return func(*args)

    def __call__(self):
        if len(self.traverse_subpath) > 0:
            return self.handle_subpath()
        return super(SenaiteTheme, self).__call__()

    @memoize_contextless
    def theme_config(self):
        return theme.CONFIG

    @memoize_contextless
    def theme_json_config(self):
        return theme.CONFIG_JSON

    @memoize_contextless
    def icon(self, name):
        config = self.theme_config()
        icons = config.get("icons")
        return icons.get(name, "")
