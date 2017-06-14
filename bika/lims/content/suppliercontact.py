# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

"""The contact person at a reference supplier organisation.
"""
from AccessControl import ClassSecurityInfo
from Products.Archetypes.ArchetypeTool import registerType
from bika.lims.config import PROJECTNAME
from bika.lims.content.person import Person
from bika.lims.content.schema.suppliercontact import schema


class SupplierContact(Person):
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


registerType(SupplierContact, PROJECTNAME)
