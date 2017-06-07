# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""SamplesFolder is a fake folder to live in the nav bar.  It has
view from browser/sample.py/SamplesView wired to it.
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.samplesfolder import schema
from bika.lims.interfaces import IHaveNoBreadCrumbs, ISamplesFolder
from plone.app.folder import folder
from zope.interface import implements


class SamplesFolder(folder.ATFolder):
    implements(ISamplesFolder, IHaveNoBreadCrumbs)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

atapi.registerType(SamplesFolder, PROJECTNAME)
