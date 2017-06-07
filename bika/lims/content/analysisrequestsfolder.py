# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""AnalysisRequestsFolder is a fake folder to live in the nav bar.  It has
view from browser/analysisrequest.py wired to it.
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IAnalysisRequestsFolder, IHaveNoBreadCrumbs
from plone.app.folder import folder
from zope.interface import implements

schema = folder.ATFolderSchema.copy()

class AnalysisRequestsFolder(folder.ATFolder):
    implements(IAnalysisRequestsFolder, IHaveNoBreadCrumbs)
    schema = schema
    displayContentsTab = False
    security = ClassSecurityInfo()

schemata.finalizeATCTSchema(schema, folderish = True, moveDiscussion = False)

atapi.registerType(AnalysisRequestsFolder, PROJECTNAME)
