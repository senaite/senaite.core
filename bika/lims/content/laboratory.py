# -*- coding: utf-8 -*-
# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from AccessControl import ClassSecurityInfo
from Products.Archetypes.ArchetypeTool import registerType
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import UniqueObject
from Products.CMFPlone.utils import safe_unicode
from bika.lims import bikaMessageFactory as _
from bika.lims.config import PROJECTNAME
from bika.lims.content.organisation import Organisation
from bika.lims.content.schema.laboratory import schema


class Laboratory(UniqueObject, Organisation):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    security.declareProtected(View, 'getSchema')

    def getSchema(self):
        return self.schema

    def Title(self):
        title = self.getName() and self.getName() or _("Laboratory")
        return safe_unicode(title).encode('utf-8')


registerType(Laboratory, PROJECTNAME)
