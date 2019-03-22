# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import ISupplyOrderFolder
from plone.app.folder import folder
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from zope.interface import implements


schema = folder.ATFolderSchema.copy()


class SupplyOrderFolder(folder.ATFolder):
    implements(ISupplyOrderFolder)
    schema = schema
    displayContentsTab = False
    security = ClassSecurityInfo()


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
atapi.registerType(SupplyOrderFolder, PROJECTNAME)
