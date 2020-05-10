# -*- coding: utf-8 -*-

from zope.viewlet.interfaces import IViewletManager


class ISidebar(IViewletManager):
    """A viewlet manager that sits left from the content
    """


class IListingTableTitle(IViewletManager):
    """A viewlet manager that sits in the title slot
    """


class IListingTableDescription(IViewletManager):
    """A viewlet manager that sits in the description slot
    """


class IAboveListingTable(IViewletManager):
    """A viewlet manager that sits above listing tables
    """


class IBelowListingTable(IViewletManager):
    """A viewlet manager that sits below listing tables
    """
