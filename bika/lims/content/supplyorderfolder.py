# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""Supply Order Folder contains Supply Orders
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes.ArchetypeTool import registerType
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.supplyorderfolder import schema
from bika.lims.interfaces import IHaveNoBreadCrumbs, ISupplyOrderFolder
from plone.app.folder import folder
from zope.interface import implements


class SupplyOrderFolder(folder.ATFolder):
    implements(ISupplyOrderFolder, IHaveNoBreadCrumbs)
    schema = schema
    displayContentsTab = False
    security = ClassSecurityInfo()


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

registerType(SupplyOrderFolder, PROJECTNAME)
