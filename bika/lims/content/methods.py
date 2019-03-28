# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IHaveNoBreadCrumbs
from bika.lims.interfaces import IMethods
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from Products.Archetypes.public import registerType
from Products.ATContentTypes.content import schemata
from zope.interface.declarations import implements

schema = ATFolderSchema.copy()


class Methods(ATFolder):
    """Root folder for Reference Samples
    """
    implements(IMethods, IHaveNoBreadCrumbs)

    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

registerType(Methods, PROJECTNAME)
