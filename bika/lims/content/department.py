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

"""Department - the department in the laboratory.
"""
from Products.Archetypes.public import *
from Products.Archetypes.references import HoldingReference
from Products.CMFCore.utils import getToolByName
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from AccessControl import ClassSecurityInfo
import sys
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from zope.interface import implements
from bika.lims.interfaces import IDepartment, IDeactivable

schema = BikaSchema.copy() + Schema((
    ReferenceField('Manager',
        vocabulary = 'getContacts',
        vocabulary_display_path_bound = sys.maxint,
        allowed_types = ('LabContact',),
        referenceClass = HoldingReference,
        relationship = 'DepartmentLabContact',
        widget = ReferenceWidget(
            checkbox_bound = 0,
            label=_("Manager"),
            description = _(
                "Select a manager from the available personnel configured under the "
                "'lab contacts' setup item. Departmental managers are referenced on "
                "analysis results reports containing analyses by their department."),
        ),
    ),
    ComputedField('ManagerName',
        expression = "context.getManager() and context.getManager().getFullname() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ManagerPhone',
        expression = "context.getManager() and context.getManager().getBusinessPhone() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
    ComputedField('ManagerEmail',
        expression = "context.getManager() and context.getManager().getEmailAddress() or ''",
        widget = ComputedWidget(
            visible = False,
        ),
    ),
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
