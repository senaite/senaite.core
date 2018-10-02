# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.ATContentTypes.content import schemata
from Products.Archetypes.public import registerType
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IMethods
from plone.app.folder.folder import ATFolder, ATFolderSchema
from zope.interface.declarations import implements

schema = ATFolderSchema.copy()


class Methods(ATFolder):
    implements(IMethods)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)
registerType(Methods, PROJECTNAME)
