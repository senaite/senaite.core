# -*- coding: utf-8 -*-

from zope.interface import Interface


class ISenaiteCore(Interface):
    """Marker interface that defines a Zope 3 browser layer.
    """


class IShowDisplayMenu(Interface):
    """Marker interface that can be applied for contents that should display
    the "Display" menu
    """


class IShowFactoriesMenu(Interface):
    """Marker interface that can be applied for contents that should display
    the "Add" menu
    """
