# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
