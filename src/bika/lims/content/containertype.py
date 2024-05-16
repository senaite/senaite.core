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


from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IContainerType
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IDeactivable
from zope.interface import implements

schema = BikaSchema.copy() + Schema((
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'


# TODO: Migrated to DX - https://github.com/senaite/senaite.core/pull/2540
class ContainerType(BaseContent):
    implements(IContainerType, IDeactivable)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from senaite.core.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getContainers(self):
        """Return a list of all containers of this type
        """
        _containers = []
        for container in self.bika_setup.bika_containers.objectValues():
            containertype = container.getContainerType()
            if containertype and containertype.UID() == self.UID():
                _containers.append(container)
        return _containers


registerType(ContainerType, PROJECTNAME)
