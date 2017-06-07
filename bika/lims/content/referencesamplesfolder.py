# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""ReferenceSamplesFolder is a fake folder to live in the nav bar.  It has
view from browser/referencesample.py wired to it.
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IHaveNoBreadCrumbs, IReferenceSamplesFolder
from plone.app.folder import folder
from zope.interface import implements

schema = folder.ATFolderSchema.copy()


class ReferenceSamplesFolder(folder.ATFolder):
    implements(IReferenceSamplesFolder, IHaveNoBreadCrumbs)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

atapi.registerType(ReferenceSamplesFolder, PROJECTNAME)
