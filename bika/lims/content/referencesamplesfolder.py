# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IHaveNoBreadCrumbs
from bika.lims.interfaces import IReferenceSamplesFolder
from plone.app.folder import folder
from plone.app.folder.folder import ATFolder
from Products.Archetypes.public import registerType
from Products.ATContentTypes.content import schemata
from zope.interface import implements


schema = folder.ATFolderSchema.copy()


class ReferenceSamplesFolder(ATFolder):
    """Root folder for Reference Samples
    """
    implements(IReferenceSamplesFolder, IHaveNoBreadCrumbs)

    schema = schema
    displayContentsTab = False
    security = ClassSecurityInfo()


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

registerType(ReferenceSamplesFolder, PROJECTNAME)
