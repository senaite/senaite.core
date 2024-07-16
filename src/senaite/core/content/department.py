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
from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IDeactivable
from bika.lims.interfaces import IHaveDepartment
from plone.autoform import directives
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.catalog import CONTACT_CATALOG
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.config.widgets import get_labcontact_columns
from senaite.core.content.base import Container
from senaite.core.interfaces import IDepartment
from senaite.core.schema import UIDReferenceField
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from zope import schema
from zope.interface import Invalid
from zope.interface import implementer
from zope.interface import invariant


class IDepartmentSchema(model.Schema):
    """Schema interface
    """

    title = schema.TextLine(
        title=_(
            u"title_department_title",
            default=u"Name"
        ),
        description=_(
            u"description_department_title",
            default=u"Name of the department"
        ),
        required=True,
    )

    description = schema.Text(
        title=_(
            u"title_department_description",
            default=u"Description"
        ),
        required=False,
    )

    # Department ID
    directives.widget("department_id",
                      before_text_input="ID",
                      before_css_input="text-secondary",
                      widget_css_display="text-primary text-monospace",
                      widget_css_input="text-primary text-monospace",
                      after_text_input="<i class='fas fa-id-card'></i>",
                      after_css_input="text-primary")
    department_id = schema.TextLine(
        title=_(
            u"title_department_id",
            default=u"Department ID"
        ),
        description=_(
            u"description_department_id",
            default=u"Please provide a unique department identifier"
        ),
        required=True,
    )

    directives.widget(
        "manager",
        UIDReferenceWidgetFactory,
        catalog=CONTACT_CATALOG,
        query={
            "portal_type": "LabContact",
            "is_active": True,
            "sort_on": "title",
            "sort_order": "ascending",
        },
        display_template="<a href='${url}'>${getFullname}</a>",
        columns=get_labcontact_columns,
        limit=5,
    )
    manager = UIDReferenceField(
        title=_(
            u"label_department_manager",
            default=u"Manager"
        ),
        description=_(
            u"description_department_manager",
            default=u"Select a manager from the available personnel "
                    u"configured under the 'lab contacts' setup item. "
                    u"Departmental managers are referenced on analysis "
                    u"results reports containing analyses by their department."
        ),
        allowed_types=("LabContact", ),
        relationship="DepartmentLabContact",
        multi_valued=False,
        required=True,
    )

    @invariant
    def validate_department_id(data):
        """Checks if the department ID is unique
        """
        dpt_id = data.department_id
        context = getattr(data, "__context__", None)
        if context and context.department_id == dpt_id:
            # nothing changed
            return
        query = {
            "portal_type": "Department",
            "department_id": dpt_id,
        }
        results = api.search(query, catalog=SETUP_CATALOG)
        if len(results) > 0:
            raise Invalid(_("Department ID must be unique"))


@implementer(IDepartment, IDepartmentSchema, IHaveDepartment, IDeactivable)
class Department(Container):
    """Department
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def getDepartmentID(self):
        accessor = self.accessor("department_id")
        value = accessor(self) or ""
        return value.encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setDepartmentID(self, value):
        mutator = self.mutator("department_id")
        mutator(self, api.safe_unicode(value))

    # BBB: AT schema field property
    DepartmentID = property(getDepartmentID, setDepartmentID)

    @security.protected(permissions.View)
    def getRawManager(self):
        accessor = self.accessor("manager", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getManager(self):
        accessor = self.accessor("manager")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setManager(self, value):
        mutator = self.mutator("manager")
        mutator(self, value)

    # BBB: AT schema field property
    Manager = property(getManager, setManager)
