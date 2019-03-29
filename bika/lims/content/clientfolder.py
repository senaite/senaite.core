# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

"""ClientFolder is a container for Client instances.
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IClientFolder, IHaveNoBreadCrumbs
from plone.app.folder import folder
from zope.interface import implements

schema = folder.ATFolderSchema.copy()
schema['id'].widget.visible = {'edit': 'hidden', 'view': 'invisible'}
schema['title'].widget.visible = {'edit': 'hidden', 'view': 'invisible'}


class ClientFolder(folder.ATFolder):
    implements(IClientFolder, IHaveNoBreadCrumbs)
    displayContentsTab = False
    schema = schema
    security = ClassSecurityInfo()

schemata.finalizeATCTSchema(schema, folderish=True, moveDiscussion=False)

atapi.registerType(ClientFolder, PROJECTNAME)
