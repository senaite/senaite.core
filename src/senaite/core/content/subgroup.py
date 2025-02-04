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
from plone.supermodel import model
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import ISubGroup
from zope import schema
from zope.interface import Invalid
from zope.interface import implementer
from zope.interface import invariant


class ISubGroupSchema(model.Schema):
    """Schema interface
    """

    title = schema.TextLine(
        title=_(
            "title_subgroup_title",
            default="Name"
        ),
        required=True,
    )

    description = schema.Text(
        title=_(
            "title_subgroup_description",
            default="Description"
        ),
        required=False,
    )

    sort_key = schema.Float(
        title=_(
            "title_subgroup_sort_key",
            default="Sort Key"
        ),
        description=_(
            u"description_subgroup_sort_key",
            default=u"Float value from 0.0 - 1000.0 indicating the sort order."
                    " Duplicate values are ordered alphabetically."),
        required=False,
    )

    @invariant
    def validate_sort_key(data):
        """Checks sort_key field for float value if exist
        """
        sort_key = getattr(data, "sort_key", None)
        if sort_key is None:
            return

        try:
            value = float(data.sort_key)
        except (TypeError, ValueError):
            msg = _("Validation failed: value must be float")
            raise Invalid(msg)

        if value < 0 or value > 1000:
            msg = _("Validation failed: value must be between 0 and 1000")
            raise Invalid(msg)


@implementer(ISubGroup, ISubGroupSchema, IDeactivable)
class SubGroup(Container):
    """Sub Group type
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()

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
