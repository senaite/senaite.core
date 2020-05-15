# -*- coding: utf-8 -*-

from zope.interface import Interface


class ISenaiteTheme(Interface):
    """A view that provides theme specific configuration
    """

    def theme_config():
        """The theme config object
        """

    def theme_json_config():
        """The theme config object as JSON
        """

    def icon(name):
        """The the configured icon URL
        """
