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

from Products.Five.browser import BrowserView
from zope.interface import implementer

from .interfaces import ISenaiteView


@implementer(ISenaiteView)
class SenaiteView(BrowserView):
    """A view that provides global utilities
    """

    def test(self, *args):
        """A special function, 'test', that supports if-then expressions.

        The 'test' function accepts any number of arguments. If the first
        argument is true, then the second argument is returned, otherwise if
        the third argument is true, then the fourth argument is returned, and
        so on. If there is an odd number of arguments, then the last argument
        is returned in the case that none of the tested arguments is true,
        otherwise None is returned.

        This code is taken from `RestrictedPython.Utilities`.

        Used in `main_template` to work around the following issue:
        https://community.plone.org/t/plone-5-2-1-5-2-2-page-template-issues
        """
        length = len(args)
        for i in range(1, length, 2):
            if args[i - 1]:
                return args[i]

        if length % 2:
            return args[-1]
