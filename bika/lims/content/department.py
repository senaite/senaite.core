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
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import ReferenceField
from Products.Archetypes.public import Schema
from Products.Archetypes.public import registerType
from Products.Archetypes.references import HoldingReference
from zope.interface import implements

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.catalog.bikasetup_catalog import SETUP_CATALOG
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IDeactivable
from bika.lims.interfaces import IDepartment

Manager = ReferenceField(
    'Manager',
    required=1,
    allowed_types=('LabContact',),
    referenceClass=HoldingReference,
    relationship="DepartmentLabContact",
    widget=ReferenceWidget(
        label=_("Manager"),
        description=_(
            "Select a manager from the available personnel configured under "
            "the 'lab contacts' setup item. Departmental managers are "
            "referenced on analysis results reports containing analyses by "
            "their department."),
        showOn=True,
        catalog_name=SETUP_CATALOG,
        base_query=dict(
            is_active=True,
            sort_on="sortable_title",
            sort_order="ascending",
        ),
    ),
)

schema = BikaSchema.copy() + Schema((
    Manager,
))

schema['description'].widget.visible = True
schema['description'].schemata = 'default'


class Department(BaseContent):
    implements(IDepartment, IDeactivable)
    security = ClassSecurityInfo()
    displayContentsTab = False
    schema = schema

    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from bika.lims.idserver import renameAfterCreation
        renameAfterCreation(self)


registerType(Department, PROJECTNAME)
