# -*- coding: utf-8 -*-

from zope.interface import Interface


class ISenaiteTheme(Interface):
    """A view that provides theme specific configuration
    """

    def icons():
        """Returns a dictionary of icon name -> (relative) icon url
        """

    def icon(name, **kw):
        """Returns the configured (relative) icon `src` URL
        """

    def icon_url(name, **kw):
        """Returns the configured (absolute) icon `src` URL
        """

    def icon_tag(name, **kw):
        """Returns a generated html `<img/>` tag
        """
