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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from AccessControl import ClassSecurityInfo
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.interfaces import IDeactivable
from bika.lims.interfaces import IDepartment
from bika.lims.interfaces import IHaveDepartment
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import registerType
from senaite.core.browser.widgets.referencewidget import ReferenceWidget
from senaite.core.catalog import CONTACT_CATALOG
from zope.interface import implements

DeapartmentID = StringField(
    "DepartmentID",
    required=1,
    searchable=True,
    validators=("uniquefieldvalidator", "standard_id_validator"),
    widget=StringWidget(
        label=_("Department ID"),
        description=_("Unique Department ID that identifies the department"),
    ),
)

Manager = UIDReferenceField(
    "Manager",
    required=1,
    allowed_types=("LabContact", ),
    relationship="DepartmentLabContact",
    widget=ReferenceWidget(
        label=_("label_department_manager",
                default="Manager"),
        description=_(
            "description_department_manager",
            default="Select a manager from the available personnel configured "
            "under the 'lab contacts' setup item. Departmental managers are "
            "referenced on analysis results reports containing analyses by "
            "their department."),
        catalog=CONTACT_CATALOG,
        query={
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending"
        },
        columns=[
            {"name": "getFullname", "label": _("Name")},
            {"name": "getEmailAddress", "label": _("Email")},
            {"name": "getJobTitle", "label": _("Job Title")},
        ],
    ),
)


schema = BikaSchema.copy() + Schema((
    DeapartmentID,
    Manager,
))

schema["description"].widget.visible = True
schema["description"].schemata = "default"


# TODO: Migrated to DX - https://github.com/senaite/senaite.core/pull/2471
class Department(BaseContent):
    implements(IDepartment, IHaveDepartment, IDeactivable)
    security = ClassSecurityInfo()
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from senaite.core.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getDepartment(self):
        """Used in catalog indexer

        see: bika.lims.catalog.indexers.bikasetup.py
        """
        return self


registerType(Department, PROJECTNAME)
