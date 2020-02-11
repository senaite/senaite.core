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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.CMFCore.utils import _getAuthenticatedUser
from AccessControl.User import nobody


def getAuthenticatedMember(self):
    '''
    Returns the currently authenticated member object
    or the Anonymous User.  Never returns None.
    This caches the value in the reqeust...
    '''
    if not "_c_authenticatedUser" in self.REQUEST:
        u = _getAuthenticatedUser(self)
        if u is None:
            u = nobody
        if str(u) not in ('Anonymous User',):
            self.REQUEST['_c_authenticatedUser'] = u
    else:
        u = self.REQUEST['_c_authenticatedUser']
    return self.wrapUser(u)
