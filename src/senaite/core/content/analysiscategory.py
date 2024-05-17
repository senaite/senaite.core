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
from Products.CMFCore import permissions
from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IDeactivable
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import IAnalysisCategory
from senaite.core.schema import UIDReferenceField
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from plone.autoform import directives
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


class IAnalysisCategorySchema(model.Schema):
    """Schema interface
    """

    title = schema.TextLine(
        title=_(
            "title_analysiscategory_title",
            default="Name"
        ),
        required=True,
    )

    description = schema.Text(
        title=_(
            "title_analysiscategory_description",
            default="Description"
        ),
        required=False,
    )

    comments = schema.Text(
        title=_(
            "title_analysiscategory_comments",
            default="Comments",
        ),
        description=_(
            "description_analysiscategory_comments",
            default="To be displayed below each Analysis Category "
                    "section on results reports.",
        ),
        required=False,
    )

    # Department reference
    directives.widget(
        "department",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query="get_department_query",
        columns="get_department_default_columns",
        limit=5,
    )
    department = UIDReferenceField(
        title=_(
            "title_analysiscategory_department",
            default="Department",
        ),
        description=_(
            "description_analysiscategory_department",
            default="Select the responsible department",
        ),
        allowed_types=("Department",),
        multi_valued=False,
        required=True,
    )

    sort_key = schema.Float(
        title=_(
            "title_analysiscategory_sort_key",
            default="Sort Key",
        ),
        description=_(
            "description_analysiscategory_sort_key",
            default="Float value from 0.0 - 1000.0 indicating the sort order. "
                    "Duplicate values are ordered alphabetically.",
        ),
        required=False,
    )


@implementer(IAnalysisCategory, IAnalysisCategorySchema, IDeactivable)
class AnalysisCategory(Container):
    """A container for analysis category
    """
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def getComments(self):
        accessor = self.accessor("comments")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setComments(self, value):
        mutator = self.mutator("comments")
        mutator(self, value)

    # BBB: AT schema field property
    Comments = property(getComments, setComments)

    @security.protected(permissions.View)
    def getDepartment(self):
        accessor = self.accessor("department")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setDepartment(self, value):
        mutator = self.mutator("department")
        mutator(self, value)

    # BBB: AT schema field property
    Department = property(getDepartment, setDepartment)

    @security.protected(permissions.View)
    def getSortKey(self):
        accessor = self.accessor("sort_key")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSortKey(self, value):
        mutator = self.mutator("sort_key")
        mutator(self, value)

    # BBB: AT schema field property
    SortKey = property(getSortKey, setSortKey)

    @security.private
    def get_department_query(self):
        """Return the query for the department field
        """
        return {
            "portal_type": "Department",
            "is_active": True,
            "sort_on": "title",
            "sort_order": "ascending",
        }

    @security.private
    def get_department_default_columns(self):
        """Returns the default columns for the reference dropdown
        """
        return [
            {
                "name": "Title",
                "label": _(
                    "search_result_column_title_title",
                    default="Department Name",
                ),
            }, {
                "name": "getDepartmentID",
                "label": _(
                    "search_result_column_title_department_id",
                    default="Department ID",
                ),
            },
        ]
