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


class ISampleSection(IViewletManager):
    """A viewlet manager responsible for sample sections below the header table
    """
