# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import ClassSecurityInfo
from bika.lims import PROJECTNAME
from bika.lims.interfaces import IHaveNoBreadCrumbs
from bika.lims.interfaces import IPricelistFolder
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from Products.Archetypes.public import registerType
from Products.ATContentTypes.content import schemata
from zope.interface import implements

schema = ATFolderSchema.copy()


class PricelistFolder(ATFolder):
    """Root folder for Pricelists
    """
    implements(IPricelistFolder, IHaveNoBreadCrumbs)

    schema = schema
    displayContentsTab = False
    security = ClassSecurityInfo()


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

registerType(PricelistFolder, PROJECTNAME)
