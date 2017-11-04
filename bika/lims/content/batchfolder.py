# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""BatchFolder contains AR Batches.
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IBatchFolder, IHaveNoBreadCrumbs
from plone.app.folder import folder
from zope.interface import implements

schema = folder.ATFolderSchema.copy()


class BatchFolder(folder.ATFolder):
    implements(IBatchFolder, IHaveNoBreadCrumbs)
    schema = schema
    displayContentsTab = False
    security = ClassSecurityInfo()

schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

atapi.registerType(BatchFolder, PROJECTNAME)
