# -*- coding: utf-8 -*-
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from AccessControl import ClassSecurityInfo
from Products.Archetypes import listTypes
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import registerType
from Products.CMFCore.utils import getToolByName
from bika.lims import PROJECTNAME
from bika.lims.content.schema.identifiertype import schema
from bika.lims.interfaces import IHaveIdentifiers


class IdentifierType(BaseContent):
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
