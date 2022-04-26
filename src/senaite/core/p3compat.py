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

# Python 3 compatibility module

def cmp(a, b):
    """Polyfill for the `cmp` builtin function

    https://docs.python.org/3.0/whatsnew/3.0.html#ordering-comparisons

    The cmp() function should be treated as gone, and the __cmp__() special
    method is no longer supported. Use __lt__() for sorting, __eq__() with
    __hash__(), and other rich comparisons as needed. (If you really need the
    cmp() functionality, you could use the expression (a > b) - (a < b) as the
    equivalent for cmp(a, b).)
    """
    return (a > b) - (a < b)
