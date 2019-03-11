# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

"""The contact person at a reference supplier organisation.
"""
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from bika.lims.config import PROJECTNAME
from bika.lims.content.person import Person
from bika.lims.interfaces import IDeactivable
from zope.interface import implements

schema = Person.schema.copy()

schema['JobTitle'].schemata = 'default'
schema['Department'].schemata = 'default'

schema['id'].schemata = 'default'
schema['id'].widget.visible = False
# Don't make title required - it will be computed from the Person's
# Fullname
schema['title'].schemata = 'default'
schema['title'].required = 0
schema['title'].widget.visible = False

class SupplierContact(Person):
    implements(IDeactivable)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True
    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

registerType(SupplierContact, PROJECTNAME)
