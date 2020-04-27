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

from bika.lims import bikaMessageFactory as _, PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IHaveIdentifiers, IDeactivable

from AccessControl import ClassSecurityInfo
from Products.Archetypes import listTypes
from Products.Archetypes.Field import LinesField
from Products.Archetypes.Schema import Schema
from Products.Archetypes.Widget import PicklistWidget
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import registerType
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

PortalTypes = LinesField(
    'PortalTypes',
    vocabulary='getPortalTypes',
    widget=PicklistWidget(
        label=_("Portal Types"),
        description=_("Select the types that this ID is used to identify."),
    ),
)

schema = BikaSchema.copy() + Schema((
    PortalTypes,
    # Attributes,
))
schema['description'].widget.visible = True
schema['description'].schemata = 'default'


class IdentifierType(BaseContent):
    implements(IDeactivable)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getPortalTypes(self):
        # cargoed from ArchetypeTool.listPortalTypesWithInterfaces because
        # portal_factory is given a FauxArchetypeTool without this method
        pt = getToolByName(self, 'portal_types')
        value = []
        for data in listTypes():
            klass = data['klass']
            for iface in [IHaveIdentifiers]:
                if iface.implementedBy(klass):
                    ti = pt.getTypeInfo(data['portal_type'])
                    if ti is not None:
                        value.append(ti)
        return [v.Title() for v in value]


registerType(IdentifierType, PROJECTNAME)
