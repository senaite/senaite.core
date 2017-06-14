# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.folder import ATFolder
from Products.Archetypes.ArchetypeTool import registerType
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.clientfolder import schema
from bika.lims.interfaces import IClientFolder, IHaveNoBreadCrumbs
from zope.interface import implements


class ClientFolder(ATFolder):
    implements(IClientFolder, IHaveNoBreadCrumbs)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

registerType(ClientFolder, PROJECTNAME)
