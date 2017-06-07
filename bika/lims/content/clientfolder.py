# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""ClientFolder is a container for Client instances.
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.clientfolder import schema
from bika.lims.interfaces import IClientFolder, IHaveNoBreadCrumbs
from plone.app.folder import folder
from zope.interface import implements


class ClientFolder(folder.ATFolder):
    implements(IClientFolder, IHaveNoBreadCrumbs)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

atapi.registerType(ClientFolder, PROJECTNAME)
