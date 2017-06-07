# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""WorksheetFolder is a container for Worksheet instances.
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.worksheetfolder import schema
from bika.lims.interfaces import IHaveNoBreadCrumbs, IWorksheetFolder
from plone.app.folder import folder
from zope.interface import implements


class WorksheetFolder(folder.ATFolder):
    implements(IWorksheetFolder, IHaveNoBreadCrumbs)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

atapi.registerType(WorksheetFolder, PROJECTNAME)
