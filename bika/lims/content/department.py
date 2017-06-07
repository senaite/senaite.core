# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""Department - the department in the laboratory.
"""
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from bika.lims.config import PROJECTNAME
from bika.lims.content.schema.department import schema
from bika.lims.interfaces import IDepartment
from zope.interface import implements


class Department(BaseContent):
    implements(IDepartment)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


registerType(Department, PROJECTNAME)
