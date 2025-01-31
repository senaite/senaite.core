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
# Copyright 2018-2024 by it's authors.
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


class ISampleTitle(IViewletManager):
    """A viewlet manager in the sample view title section
    """


class ISampleDescription(IViewletManager):
    """A viewlet manager in the sample view below the title
    """


class ISampleHeader(IViewletManager):
    """A viewlet manager in sample view above the sections
    """


class IAboveSampleSection(IViewletManager):
    """A viewlet manager in sample view above analyses sections
    """


class ISampleSection(IViewletManager):
    """A viewlet manager in sample view to show lab/field analyses sections
    """


class IBelowSampleSection(IViewletManager):
    """A viewlet manager in sample view below analyses sections
    """


class ISampleFooter(IViewletManager):
    """A viewlet manager in sample view below the sections
    """
