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
from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IDeactivable
from plone.autoform import directives
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.config.widgets import get_default_columns
from senaite.core.content.base import Container
from senaite.core.interfaces import ISampleTemplate
from senaite.core.schema import UIDReferenceField
from senaite.core.schema.fields import DataGridRow
from senaite.core.z3cform.widgets.datagrid import DataGridWidgetFactory
from senaite.core.z3cform.widgets.listing.widget import ListingWidgetFactory
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from zope import schema
from zope.interface import Interface
from zope.interface import implementer


class IServiceRecord(Interface):
    """Record schema for selected services and partitions
    """
    uid = schema.TextLine(title=u"Service UID")
    hidden = schema.Bool(title=u"Hidden")
    part_id = schema.TextLine(title=u"Partition ID")


class IPartitionRecord(Interface):
    """DataGrid Row for Sample Partition Schema
    """

    # PARTITION
    directives.widget("part_id",
                      style=u"width:100px!important")
    part_id = schema.TextLine(
        title=_(
            u"label_sampletemplate_partition_part_id",
            default=u"Partition ID"
        ),
        required=False,
        default=u"part-1")

    # CONTAINER
    directives.widget(
        "container",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "portal_type": "SampleContainer",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        },
        display_template="<a href='${url}'>${Title}</a>",
        columns=get_default_columns,
        limit=5)
    container = UIDReferenceField(
        title=_(
            u"label_sampletemplate_partition_container",
            default=u"Container"
        ),
        allowed_types=("SampleContainer", ),
        multi_valued=False,
        required=False)

    # PRESERVATION
    directives.widget(
        "preservation",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "portal_type": "Preservation",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        },
        display_template="<a href='${url}'>${Title}</a>",
        columns=get_default_columns,
        limit=5)
    preservation = UIDReferenceField(
        title=_(
            u"label_sampletemplate_partition_preservation",
            default=u"Preservation"
        ),
        allowed_types=("SamplePreservation", ),
        multi_valued=False,
        required=False)

    # SAMPLE TYPE
    directives.widget(
        "sampletype",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "portal_type": "SampleType",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        },
        display_template="<a href='${url}'>${Title}</a>",
        columns=get_default_columns,
        limit=5)
    sampletype = UIDReferenceField(
        title=_(
            u"label_sampletemplate_partition_sampletype",
            default=u"Sample Type"
        ),
        allowed_types=("SampleType", ),
        multi_valued=False,
        required=False)


class ISampleTemplateSchema(model.Schema):
    """Schema interface
    """
    model.fieldset(
        "partitions",
        label=_(u"Partitions"),
        fields=[
            "partitions",
        ]
    )

    model.fieldset(
        "analyses",
        label=_(u"Analyses"),
        fields=[
            "services",
        ]
    )

    title = schema.TextLine(
        title=_(
            u"title_sampletemplate_title",
            default=u"Name"
        ),
        required=True,
    )

    description = schema.Text(
        title=_(
            u"title_sampletemplate_description",
            default=u"Description"
        ),
        required=False,
    )

    directives.widget(
        "samplepoint",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "portal_type": "SamplePoint",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        },
        display_template="<a href='${url}'>${Title}</a>",
        columns=get_default_columns,
        limit=5,
    )
    samplepoint = UIDReferenceField(
        title=_(
            u"label_sampletemplate_samplepoint",
            default=u"Sample Point"
        ),
        description=_(
            u"description_sampletemplate_samplepoint",
            default=u"Select the sample point for this template"
        ),
        allowed_types=("SamplePoint", ),
        multi_valued=False,
        required=False,
    )

    directives.widget(
        "sampletype",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "portal_type": "SampleType",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        },
        display_template="<a href='${url}'>${Title}</a>",
        columns=get_default_columns,
        limit=5,
    )
    sampletype = UIDReferenceField(
        title=_(
            u"label_sampletemplate_sampletype",
            default=u"Sample Type"
        ),
        description=_(
            u"description_sampletemplate_sampletype",
            default=u"Select the sample type for this template"
        ),
        allowed_types=("SampleType", ),
        multi_valued=False,
        required=False,
    )

    composite = schema.Bool(
        title=_(
            u"title_sampletemplate_composite",
            default=u"Composite"
        ),
        description=_(
            u"description_sampletemplate_composite",
            default=u"Select if the sample is a mix of sub samples"
        ),
        required=False,
    )

    directives.widget(
        "partitions",
        DataGridWidgetFactory,
        allow_insert=True,
        allow_delete=True,
        allow_reorder=True,
        auto_append=True)
    partitions = schema.List(
        title=_(
            u"label_sampletemplate_partitions",
            default=u"Partitions"),
        description=_(
            u"description_sampletemplate_partitions",
            default=u"Each line defines a new partition identified by the "
                    u"'Partition ID'"),
        value_type=DataGridRow(
            title=u"Partition Scheme",
            schema=IPartitionRecord),
        required=True,
        default=[],
    )

    directives.widget("services",
                      ListingWidgetFactory,
                      listing_view="sampletemplate_services_widget")
    services = schema.List(
        title=_(
            u"title_sampletemplate_services",
            default=u"Services"
        ),
        description=_(
            u"description_sampletemplate_services",
            default=u"Select the services for this template"
        ),
        value_type=DataGridRow(schema=IServiceRecord),
        default=[],
        required=True,
    )


@implementer(ISampleTemplate, ISampleTemplateSchema, IDeactivable)
class SampleTemplate(Container):
    """SampleTemplate
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def getPartitions(self):
        accessor = self.accessor("partitions")
        return accessor(self) or []
#
#    @security.protected(permissions.ModifyPortalContent)
#    def setSampleTemplateID(self, value):
#        mutator = self.mutator("sampleTemplate_id")
#        mutator(self, api.safe_unicode(value))
#
#    # BBB: AT schema field property
#    SampleTemplateID = property(getSampleTemplateID, setSampleTemplateID)
#
#    @security.protected(permissions.View)
#    def getRawManager(self):
#        accessor = self.accessor("manager", raw=True)
#        return accessor(self)
#
#    @security.protected(permissions.View)
#    def getManager(self):
#        accessor = self.accessor("manager")
#        return accessor(self)
#
#    @security.protected(permissions.ModifyPortalContent)
#    def setManager(self, value):
#        mutator = self.mutator("manager")
#        mutator(self, value)
#
#    # BBB: AT schema field property
#    Manager = property(getManager, setManager)
