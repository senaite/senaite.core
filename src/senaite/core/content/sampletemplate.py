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
from senaite.core.config.widgets import get_default_columns
from senaite.core.content.base import Container
from senaite.core.content.mixins import ClientAwareMixin
from senaite.core.interfaces import ISampleTemplate
from senaite.core.schema import UIDReferenceField
from senaite.core.schema.fields import DataGridRow
from senaite.core.z3cform.widgets.datagrid import DataGridWidgetFactory
from senaite.core.z3cform.widgets.listing.widget import ListingWidgetFactory
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from zope import schema
from zope.deprecation import deprecate
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
        columns=get_default_columns)
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
            "portal_type": "SamplePreservation",
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        },
        display_template="<a href='${url}'>${Title}</a>",
        columns=get_default_columns)
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
        columns=get_default_columns)
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

    # Fieldset "Partitions"
    model.fieldset(
        "partitions",
        label=_(u"fieldset_sampletemplate_partitions",
                default=u"Partitions"),
        fields=[
            "partitions",
            "auto_partition",
        ]
    )

    # Fieldset "Analyses"
    model.fieldset(
        "analyses",
        label=_(u"fieldset_sampletemplate_analyses",
                default=u"Analyses"),
        fields=[
            "services",
        ]
    )

    # Title
    title = schema.TextLine(
        title=_(u"title_sampletemplate_title",
                default=u"Name"),
        required=True)

    # Description
    description = schema.Text(
        title=_(u"title_sampletemplate_description",
                default=u"Description"),
        required=False)

    # Sample Point
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
        columns=get_default_columns)
    samplepoint = UIDReferenceField(
        title=_(u"label_sampletemplate_samplepoint",
                default=u"Sample Point"),
        description=_(u"description_sampletemplate_samplepoint",
                      default=u"Select the sample point for this template"),
        allowed_types=("SamplePoint", ),
        multi_valued=False,
        required=False)

    # Sample Type
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
        columns=get_default_columns)
    sampletype = UIDReferenceField(
        title=_(u"label_sampletemplate_sampletype",
                default=u"Sample Type"),
        description=_(u"description_sampletemplate_sampletype",
                      default=u"Select the sample type for this template"),
        allowed_types=("SampleType", ),
        multi_valued=False,
        required=False)

    # Composite
    composite = schema.Bool(
        title=_(u"title_sampletemplate_composite",
                default=u"Composite"),
        description=_(u"description_sampletemplate_composite",
                      default=u"Select if the sample is a mix of sub samples"),
        default=False,
        required=False)

    # Sampling Required
    sampling_required = schema.Bool(
        title=_(u"title_sampletemplate_sampling_required",
                default=u"Sample collected by the laboratory"),
        description=_(u"description_sampletemplate_sampling_required",
                      default=u"Enable sampling workflow for the created "
                              u"samples"),
        default=False,
        required=False)

    # Partitions (Data Grid)
    directives.widget(
        "partitions",
        DataGridWidgetFactory,
        allow_insert=False,  # only auto append
        allow_delete=True,
        allow_reorder=True,
        auto_append=True)
    partitions = schema.List(
        title=_(u"label_sampletemplate_partitions",
                default=u"Partitions"),
        description=_(u"description_sampletemplate_partitions",
                      default=u"Each line defines a new partition "
                      u"identified by the 'Partition ID'"),
        value_type=DataGridRow(
            title=u"Partition Scheme",
            schema=IPartitionRecord),
        required=True,
        default=[])

    # Auto Partition
    auto_partition = schema.Bool(
        title=_(u"title_sampletemplate_auto_partition",
                default=u"Auto-partition on sample reception"),
        description=_(u"description_sampletemplate_auto_partition",
                      default=u"Automatically redirect the user to the "
                              u"partitions view when the sample is received"),
        default=False,
        required=False)

    # Services
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
class SampleTemplate(Container, ClientAwareMixin):
    """SampleTemplate
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def getRawSamplePoint(self):
        accessor = self.accessor("samplepoint", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getSamplePoint(self):
        samplepoint = self.getRawSamplePoint()
        if not samplepoint:
            return None
        return api.get_object(samplepoint)

    @security.protected(permissions.ModifyPortalContent)
    def setSamplePoint(self, value):
        mutator = self.mutator("samplepoint")
        mutator(self, value)

    @deprecate("deprecated since SENAITE 2.6: Use getRawSamplePoint() instead")
    @security.protected(permissions.View)
    def getSamplePointUID(self):
        return self.getRawSamplePoint()

    # BBB: AT schema field property
    SamplePoint = property(getSamplePoint, setSamplePoint)
    SamplePointUID = property(getRawSamplePoint)

    @security.protected(permissions.View)
    def getRawSampleType(self):
        accessor = self.accessor("sampletype", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getSampleType(self):
        sampletype = self.getRawSampleType()
        if not sampletype:
            return None
        return api.get_object(sampletype)

    @security.protected(permissions.ModifyPortalContent)
    def setSampleType(self, value):
        mutator = self.mutator("sampletype")
        mutator(self, value)

    # BBB: AT schema field property
    SampleType = property(getSampleType, setSampleType)

    @security.protected(permissions.View)
    def getComposite(self):
        accessor = self.accessor("composite")
        return bool(accessor(self))

    @security.protected(permissions.ModifyPortalContent)
    def setComposite(self, value):
        mutator = self.mutator("composite")
        mutator(self, bool(value))

    # BBB: AT schema field property
    Composite = property(getComposite, setComposite)

    @security.protected(permissions.View)
    def getSamplingRequired(self):
        accessor = self.accessor("sampling_required")
        return bool(accessor(self))

    @security.protected(permissions.ModifyPortalContent)
    def setSamplingRequired(self, value):
        mutator = self.mutator("sampling_required")
        mutator(self, bool(value))

    @security.protected(permissions.View)
    def getSamplingRequiredDefaultValue(self):
        """Get the setup if the sampling workflow is enabled or not
        """
        bikasetup = api.get_bika_setup()
        return bikasetup.getSamplingWorkflowEnabled()

    # BBB: AT schema field property
    SamplingRequired = property(getSamplingRequired, setSamplingRequired)

    @security.protected(permissions.View)
    def getPartitions(self):
        accessor = self.accessor("partitions")
        records = accessor(self) or []

        # UIDReference sub-fields are stored as a list!
        # See https://github.com/senaite/senaite.core/pull/2630
        def first(record, subfield):
            items = record.get(subfield)
            return items[0] if items else ""

        partitions = []
        for record in records:
            partition = record.copy()
            partition.update({
                "sampletype": first(record, "sampletype"),
                "container": first(record, "container"),
                "preservation": first(record, "preservation"),
            })
            partitions.append(partition)

        return partitions

    @security.protected(permissions.ModifyPortalContent)
    def setPartitions(self, value):
        """Set partitions for the template
        """
        if not isinstance(value, (list, dict)):
            raise TypeError(
                "Expected a dict or list, got %r" % type(value))
        if isinstance(value, dict):
            value = [value]
        records = []
        for v in value:
            part_id = v.get("part_id", "")
            container = v.get("container", "")
            preservation = v.get("preservation", "")
            sampletype = v.get("sampletype", "")

            # ensure UIDs for reference fields
            if container:
                container = api.get_uid(container)
            if preservation:
                preservation = api.get_uid(preservation)
            if sampletype:
                sampletype = api.get_uid(sampletype)

            records.append({
                "part_id": part_id,
                "container": container,
                "preservation": preservation,
                "sampletype": sampletype,
            })
        mutator = self.mutator("partitions")
        mutator(self, records)

    # BBB: AT schema field property
    Partitions = property(getPartitions, setPartitions)

    @security.protected(permissions.View)
    def getAutoPartition(self):
        accessor = self.accessor("auto_partition")
        return bool(accessor(self))

    @security.protected(permissions.ModifyPortalContent)
    def setAutoPartition(self, value):
        mutator = self.mutator("auto_partition")
        mutator(self, bool(value))

    # BBB: AT schema field property
    AutoPartition = property(getAutoPartition, setAutoPartition)

    @security.protected(permissions.View)
    def getRawServices(self):
        """Return the raw value of the services field

        >>> self.getRawServices()
        [{'uid': '...', 'part_id': 'part-1', 'hidden': False}, ...]

        :returns: List of dicts including `uid`, `hidden` and `part_id`
        """
        accessor = self.accessor("services")
        return accessor(self) or []

    @security.protected(permissions.View)
    def getServices(self):
        """Returns a list of service objects

        >>> self.getServices()
        [<AnalysisService at ...>,  <AnalysisService at ...>, ...]

        :returns: List of analysis service objects
        """
        records = self.getRawServices()
        service_uids = map(lambda r: r.get("uid"), records)
        return list(map(api.get_object, service_uids))

    @security.protected(permissions.ModifyPortalContent)
    def setServices(self, value):
        """Set services for the template

        This method accepts either a list of analysis service objects, a list
        of analysis service UIDs or a list of analysis profile service records
        containing the keys `uid`, `hidden` and `part_id`:

        >>> self.setServices([<AnalysisService at ...>, ...])
        >>> self.setServices(['353e1d9bd45d45dbabc837114a9c41e6', '...', ...])
        >>> self.setServices([{'hidden': False, 'uid': '...'}, ...])

        Raises a TypeError if the value does not match any allowed type.
        """
        if not isinstance(value, list):
            value = [value]

        records = []
        for v in value:
            uid = ""
            hidden = False
            part_id = ""
            if isinstance(v, dict):
                uid = api.get_uid(v.get("uid"))
                hidden = v.get("hidden",
                               api.get_object(uid).getHidden())
                part_id = v.get("part_id", "")
            elif api.is_object(v):
                uid = api.get_uid(v)
                hidden = v.getHidden()
            elif api.is_uid(v):
                obj = api.get_object(v)
                uid = v
                hidden = obj.getHidden()
            else:
                raise TypeError(
                    "Expected object, uid or record, got %r" % type(v))
            records.append({
                "uid": uid,
                "hidden": hidden,
                "part_id": part_id,
            })

        mutator = self.mutator("services")
        mutator(self, records)

    # BBB: AT schema field property
    Services = property(getServices, setServices)

    @deprecate("deprecated since SENAITE 2.6: Use getRawServices() instead")
    @security.protected(permissions.View)
    def getAnalysisServicesSettings(self):
        """BBB: Return the settings for all assigned services

        :returns: List of dicts including `uid`, `hidden` and `part_id`
        """
        # Note: We store the selected service UIDs, hidden and part_id
        # settings in the `services` field. Therefore, we can just return the
        # raw value.
        return self.getRawServices()

    @security.protected(permissions.ModifyPortalContent)
    def setAnalysisServicesSettings(self, settings):
        """BBB: Update settings for all assigned service UIDs

        This method expects a list of dictionaries containing the service
        `uid`, `part_id` and the `hidden` setting.

        This is basically the same format as stored in the `services` field!

        However, we want to just update the settings for selected service UIDs"

        >>> settings =  [{'uid': '...', 'hidden': False, 'part_id': 'part-1'}]
        >>> setAnalysisServicesSettings(settings)
        """
        if not isinstance(settings, list):
            settings = [settings]

        by_uid = self.get_services_by_uid()

        for setting in settings:
            if not isinstance(setting, dict):
                raise TypeError(
                    "Expected a record containing `uid`, `hidden` and"
                    "`partition`, got %s" % type(setting))
            uid = api.get_uid(setting.get("uid"))
            hidden = setting.get("hidden", api.get_object(uid).getHidden())
            part_id = setting.get("part_id", "")

            if not uid:
                raise ValueError("UID is missing in setting %r" % setting)

            record = by_uid.get(api.get_uid(uid))
            if not record:
                continue
            record["hidden"] = hidden
            record["part_id"] = part_id

        # set back the new services
        self.setServices(by_uid.values())

    @security.protected(permissions.View)
    def getAnalysisServiceSettings(self, service):
        """Returns the settings for a single service
        """
        uid = api.get_uid(service)
        by_uid = self.get_services_by_uid()
        record = by_uid.get(uid, {
            "uid": uid,
            "part_id": "",
            "hidden": False,
        })
        return record

    @security.protected(permissions.View)
    def isAnalysisServiceHidden(self, service):
        """Check if the service is configured as hidden
        """
        uid = api.get_uid(service)
        services = self.get_services_by_uid()
        record = services.get(uid)
        if not record:
            obj = api.get_object(service)
            return obj.getRawHidden()
        return record.get("hidden", False)

    @security.protected(permissions.View)
    def getAnalysisServicePartitionID(self, service):
        """Get the assigned parition for the service
        """
        uid = api.get_uid(service)
        services = self.get_services_by_uid()
        record = services.get(uid)
        if not record:
            return ""
        return record.get("part_id", "")

    @security.protected(permissions.View)
    def getAnalysisServiceUIDs(self):
        """Returns a list of all assigned service UIDs
        """
        services = self.getRawServices()
        return list(map(lambda record: record.get("uid"), services))

    @security.protected(permissions.View)
    def get_services_by_uid(self):
        """Return the selected services grouped by UID
        """
        records = {}
        for record in self.services:
            records[record.get("uid")] = record
        return records

    def remove_service(self, service):
        """Remove the service from the template

        If the service is not selected in the profile, returns False.

        NOTE: This method is used when an Analysis Service was deactivated.

        :param service: The service to be removed from this template
        :type service: AnalysisService
        :return: True if the AnalysisService has been removed successfully
        """
        # get the UID of the service that should be removed
        uid = api.get_uid(service)
        # get the current raw value of the services field.
        current_services = self.getRawServices()
        # filter out the UID of the service
        new_services = filter(
            lambda record: record.get("uid") != uid, current_services)

        # check if the service was removed or not
        current_services_count = len(current_services)
        new_services_count = len(new_services)

        if current_services_count == new_services_count:
            # service was not part of the profile
            return False

        # set the new services
        self.setServices(new_services)

        return True
