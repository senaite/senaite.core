# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

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
