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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.config import PROJECTNAME
from bika.lims.interfaces import IReflexRuleFolder
from bika.lims.permissions import ManageBika, AddReflexRule
from bika.lims.utils import get_link
from bika.lims.utils import get_link_for
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema
from senaite.core.interfaces import IHideActionsMenu
from zope.interface.declarations import implements

schema = ATFolderSchema.copy()


class ReflexRuleFolder(ATFolder):
    implements(IReflexRuleFolder, IHideActionsMenu)
    displayContentsTab = False
    schema = schema


schemata.finalizeATCTSchema(
    schema,
    folderish=True,
    moveDiscussion=False)

atapi.registerType(ReflexRuleFolder, PROJECTNAME)
