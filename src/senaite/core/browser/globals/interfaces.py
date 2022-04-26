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

from zope.interface import Interface


class ISenaiteView(Interface):
    """A view that provides global utilities
    """

    def test(*args):
        """A special function, 'test', that supports if-then expressions.

        This code is taken from `RestrictedPython.Utilities`.
        https://community.plone.org/t/plone-5-2-1-5-2-2-page-template-issues
        """


class ISenaiteTheme(Interface):
    """A view that provides theme specific configuration
    """

    def icons():
        """Returns a dictionary of icon name -> (relative) icon url
        """

    def icon_data(name, **kw):
        """Returns the raw icon data
        """

    def icon(name, **kw):
        """Returns the icon as data stream
        """

    def icon_path(name, **kw):
        """Returns the configured (relative) icon `src` URL
        """

    def icon_url(name, **kw):
        """Returns the configured (absolute) icon `src` URL
        """

    def icon_tag(name, **kw):
        """Returns a generated html `<img/>` tag
        """


class IIconProvider(Interface):
    """Subsription Adapter to provide custom icons
    """

    def icons():
        """Returns a dictionary of icon name -> file path
        """
