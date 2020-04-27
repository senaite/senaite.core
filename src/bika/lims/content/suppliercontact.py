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

from AccessControl import ClassSecurityInfo
from bika.lims.config import PROJECTNAME
from bika.lims.content.person import Person
from bika.lims.interfaces import IDeactivable
from zope.interface import implements
from Products.Archetypes.public import registerType

schema = Person.schema.copy()

schema["JobTitle"].schemata = "default"
schema["Department"].schemata = "default"

schema["id"].schemata = "default"
schema["id"].widget.visible = False
# Don"t make title required - it will be computed from the Person"s
# Fullname
schema["title"].schemata = "default"
schema["title"].required = 0
schema["title"].widget.visible = False


class SupplierContact(Person):
    """Supplier Contact content
    """
    implements(IDeactivable)

    _at_rename_after_creation = True
    displayContentsTab = False
    isPrincipiaFolderish = 0
    schema = schema
    security = ClassSecurityInfo()

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


registerType(SupplierContact, PROJECTNAME)
