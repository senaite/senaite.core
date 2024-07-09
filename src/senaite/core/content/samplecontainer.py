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
from plone.autoform import directives
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import ISampleContainer
from senaite.core.schema import UIDReferenceField
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from zope import schema
from zope.interface import implementer
from zope.interface import Invalid
from zope.interface import invariant


class ISampleContainerSchema(model.Schema):
    """Schema interface
    """

    title = schema.TextLine(
        title=_(
            u"title_samplecontainer_title",
            default=u"Name"
        ),
        required=True,
    )

    description = schema.Text(
        title=_(
            u"title_samplecontainer_description",
            default=u"Description"
        ),
        required=False,
    )

    # Container type reference
    directives.widget(
        "containertype",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query="get_containertype_query",
        display_template="<a href='${url}'>${title}</a>",
        columns="get_default_columns",
        limit=5,
    )
    containertype = UIDReferenceField(
        title=_(u"Container Type"),
        allowed_types=("ContainerType", ),
        multi_valued=False,
        description=_(u"Type of the container"),
        required=False,
    )

    capacity = schema.TextLine(
        title=_("Capacity"),
        description=_("Maximum possible size or volume of samples"),
        default=u"0 ml",
        required=True,
    )

    pre_preserved = schema.Bool(
        title=_("Pre-preserved"),
        description=_(
            "Check this box if this container is already preserved."
            "Setting this will short-circuit the preservation workflow "
            "for sample partitions stored in this container."),
        required=True,
    )

    @invariant
    def validate_pre_preserved(data):
        """Checks if a preservation is selected
        """
        if data.pre_preserved is False:
            return
        if not data.preservation:
            raise Invalid(_(
                "Pre-preserved containers must have a preservation selected"))

    # Preservation reference
    directives.widget(
        "preservation",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query="get_preservation_query",
        display_template="<a href='${url}'>${title}</a>",
        columns="get_default_columns",
        limit=5,
    )
    preservation = UIDReferenceField(
        title=_(u"Preservation"),
        allowed_types=("SamplePreservation", ),
        multi_valued=False,
        description=_(u"Preservation method of this container"),
        required=False,
    )

    security_seal_intact = schema.Bool(
        title=_("Security seal intact"),
        description=_(""),
        required=False,
    )


@implementer(ISampleContainer, ISampleContainerSchema, IDeactivable)
class SampleContainer(Container):
    """Sample container type
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def getContainerType(self):
        accessor = self.accessor("containertype")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setContainerType(self, value):
        mutator = self.mutator("containertype")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getCapacity(self):
        accessor = self.accessor("capacity")
        value = accessor(self) or ""
        return value.encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setCapacity(self, value):
        mutator = self.mutator("capacity")
        return mutator(self, api.safe_unicode(value))

    @security.protected(permissions.View)
    def getPrePreserved(self):
        accessor = self.accessor("pre_preserved")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setPrePreserved(self, value):
        mutator = self.mutator("pre_preserved")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getPreservation(self):
        accessor = self.accessor("preservation")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setPreservation(self, value):
        mutator = self.mutator("preservation")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getSecuritySealIntact(self):
        accessor = self.accessor("security_seal_intact")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSecuritySealIntact(self, value):
        mutator = self.mutator("security_seal_intact")
        return mutator(self, bool(value))

    @security.private
    def get_containertype_query(self):
        """Return the query for the containertype field
        """
        return {
            "portal_type": "ContainerType",
            "is_active": True,
            "sort_on": "title",
            "sort_order": "ascending",
        }

    @security.private
    def get_preservation_query(self):
        """Return the query for the preservation field
        """
        return {
            "portal_type": "SamplePreservation",
            "is_active": True,
            "sort_on": "title",
            "sort_order": "ascending",
        }

    @security.private
    def get_default_columns(self):
        """Returns the default columns for the reference dropdown
        """
        return [
            {
                "name": "title",
                "width": "30",
                "align": "left",
                "label": _(u"Title"),
            }, {
                "name": "description",
                "width": "70",
                "align": "left",
                "label": _(u"Description"),
            },
        ]
