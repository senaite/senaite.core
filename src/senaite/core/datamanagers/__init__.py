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

from bika.lims.api.security import check_permission
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from senaite.core.interfaces.datamanager import IDataManager
from zope.interface import implementer


@implementer(IDataManager)
class DataManager(object):
    """Data manager base class."""

    def __init__(self, context):
        self.context = context

    def get(self, name):
        raise NotImplementedError("Must be implemented by subclass")

    def query(self, name, default=None):
        try:
            return self.get(name)
        except AttributeError:
            return default

    def set(self, name, value):
        raise NotImplementedError("Must be implemented by subclass")

    def can_access(self):
        return check_permission(View, self.context)

    def can_write(self):
        return check_permission(ModifyPortalContent, self.context)
