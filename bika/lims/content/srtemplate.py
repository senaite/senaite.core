# -*- coding:utf-8 -*-

# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes import DisplayList
from Products.Archetypes.ArchetypeTool import registerType
from Products.Archetypes.BaseContent import BaseContent
from Products.CMFCore.utils import getToolByName
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.srtemplate import schema
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import ISamplingRoundTemplate
from bika.lims.utils import getUsers
from zope.interface import implements


class SRTemplate(BaseContent):
    implements(ISamplingRoundTemplate)
    security = ClassSecurityInfo()
    schema = schema
    displayContentsTab = False

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        renameAfterCreation(self)

    def _getSamplersDisplayList(self):
        """ Returns the available users in the system with the roles
            'LabManager' and/or 'Sampler'
        """
        return getUsers(self, ['LabManager', 'Sampler'])

    def _getDepartmentsDisplayList(self):
        """ Returns the available departments in the system. Only the
            active departments are shown, unless the object has an
            inactive department already assigned.
        """
        bsc = getToolByName(self, 'bika_setup_catalog')
        brains = bsc(portal_type='Department', inactive_state='active')
        items = [('', '')] + [(o.UID, o.Title) for o in brains]
        o = self.getDepartment()
        if o and o.UID() not in [i[0] for i in items]:
            items.append((o.UID(), o.Title()))
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return DisplayList(list(items))


registerType(SRTemplate, PROJECTNAME)
