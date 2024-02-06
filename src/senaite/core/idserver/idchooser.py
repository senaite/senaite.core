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

from bika.lims import api
from plone.app.content.namechooser import NormalizingNameChooser
from senaite.core.idserver import generateUniqueId
from senaite.core.interfaces import IAutoGenerateID
from zope.container.interfaces import INameChooser

from zope.interface import implementer


@implementer(INameChooser)
class IDChooser(object):
    """Choose a vaild ID for the given container and object
    """
    def __init__(self, context):
        self.context = context

    def chooseID(self, name, object):
        return self.chooseName(name, object)

    def checkName(self, name, object):
        return True

    def chooseName(self, name, object):
        """Choose a valid ID for the given object
        """
        if api.is_at_type(object):
            return self.chooseATName(name, object)
        return self.chooseDXName(name, object)

    def chooseATName(self, name, object):
        return generateUniqueId(object, container=self.context)

    def chooseDXName(self, name, object):
        if not IAutoGenerateID.providedBy(object):
            return self.chooseDefaultName(name, object)
        return generateUniqueId(object, container=self.context)

    def chooseDefaultName(self, name, object):
        default_chooser = NormalizingNameChooser(self.context)
        return default_chooser.chooseName(name, object)
