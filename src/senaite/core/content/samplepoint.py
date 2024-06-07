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
from plone.namedfile.field import NamedBlobFile
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.api import geo
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.content.mixins import ClientAwareMixin
from senaite.core.interfaces import ISamplePoint
from senaite.core.schema import DurationField
from senaite.core.schema import GPSCoordinatesField
from senaite.core.schema import UIDReferenceField
from senaite.core.schema.coordinatefield import SUBFIELDS as COORDINATE_FIELDS
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from zope import schema
from zope.interface import implementer


class ISamplePointSchema(model.Schema):
    """Schema interface
    """

    model.fieldset(
        "location",
        label=_(u"fieldset_samplepoint_location", default=u"Location"),
        fields=[
            "location",
            "elevation",
        ]
    )

    title = schema.TextLine(
        title=_(
            u"title_samplepoint_title",
            default=u"Name"
        ),
        required=True,
    )

    description = schema.Text(
        title=_(
            u"title_samplepoint_description",
            default=u"Description"
        ),
        required=False,
    )

    location = GPSCoordinatesField(
        title=_(
            u"title_samplepoint_location",
            default=u"Location",
        ),
        description=_(
            u"description_samplepoint_location",
            default=u"The geographical point or area from which samples are "
                    u"taken for further analysis. It plays a pivotal role in "
                    u"research as it can significantly influence the results "
                    u"and conclusions drawn from the study."
        ),
        required=False,
    )

    elevation = schema.TextLine(
        title=_(
            u'title_samplepoint_elevation',
            default=u"Elevation"
        ),
        description=_(
            u"description_samplepoint_elevation",
            default=u"The height or depth at which the sample has to be taken"
        ),
        required=False,
    )

    sampling_frequency = DurationField(
        title=_(
            u"title_samplepoint_sampling_frequency",
            default=u"Sampling Frequency"
        ),
        description=_(
            u"description_samplepoint_sampling_frequency",
            default=u"If a sample is taken periodically at this sample point, "
                    u"enter frequency here, e.g. weekly"
        ),
        required=False,
    )

    directives.widget(
        "sample_types",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "is_active": True,
            "sort_on": "title",
            "sort_order": "ascending",
        },
    )
    sample_types = UIDReferenceField(
        title=_(
            u"title_samplepoint_sampling_sample_types",
            default=u"Sample Types"
        ),
        description=_(
            u"description_samplepoint_sampling_sample_types",
            default=u"The list of sample types that can be collected "
                    u"at this sample point. The field for the selection of "
                    u"a sample point in sample creation and edit forms "
                    u"will be filtered in accordance. Still, sample points "
                    u"that do not have any sample type assigned will "
                    u"always be available for selection, regardless of the "
                    u"type."
        ),
        relationship="SamplePointSampleType",
        allowed_types=("SampleType", ),
        multi_valued=True,
        required=False,
    )

    composite = schema.Bool(
        title=_(
            u"title_samplepoint_composite",
            default=u"Composite"
        ),
        description=_(
            u"description_samplepoint_composite",
            default=u"Check this box if the samples taken at this point are "
                    u"'composite' and put together from more than one sub "
                    u"sample, e.g. several surface samples from a dam mixed "
                    u"together to be a representative sample for the dam. The "
                    u"default, unchecked, indicates 'grab' samples"
        ),
        required=False,
    )

    attachment_file = NamedBlobFile(
        title=_(
            u"title_samplepoint_attachment_file",
            default=u"Attachment"
        ),
        required=False,
    )


@implementer(ISamplePoint, ISamplePointSchema, IDeactivable)
class SamplePoint(Container, ClientAwareMixin):
    """Sample point
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def getLatitude(self):
        # mimics the coordinate field accessor
        location = self.getLocation()
        latitude = location.get("latitude")
        default_dms = dict.fromkeys(COORDINATE_FIELDS, "")
        return geo.to_latitude_dms(latitude, default=default_dms)

    @security.protected(permissions.ModifyPortalContent)
    def setLatitude(self, value):
        location = self.getLocation()
        location["latitude"] = value
        self.setLocation(location)

    # BBB: AT schema field property
    Latitude = property(getLatitude, setLatitude)

    @security.protected(permissions.View)
    def getLongitude(self):
        # mimics the coordinate field accessor
        location = self.getLocation()
        longitude = location.get("longitude")
        default_dms = dict.fromkeys(COORDINATE_FIELDS, "")
        return geo.to_longitude_dms(longitude, default=default_dms)

    @security.protected(permissions.ModifyPortalContent)
    def setLongitude(self, value):
        location = self.getLocation()
        location["longitude"] = value
        self.setLocation(location)

    # BBB: AT schema field property
    Longitude = property(getLongitude, setLongitude)

    @security.protected(permissions.View)
    def getLocation(self):
        accessor = self.accessor("location")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setLocation(self, value):
        mutator = self.mutator("location")
        mutator(self, value)

    # BBB: AT schema field property
    Location = property(getLocation, setLocation)

    @security.protected(permissions.View)
    def getElevation(self):
        accessor = self.accessor("elevation")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setElevation(self, value):
        mutator = self.mutator("elevation")
        mutator(self, value)

    # BBB: AT schema field property
    Elevation = property(getElevation, setElevation)

    @security.protected(permissions.View)
    def getSamplingFrequency(self):
        accessor = self.accessor("sampling_frequency")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSamplingFrequency(self, value):
        mutator = self.mutator("sampling_frequency")
        mutator(self, value)

    # BBB: AT schema field property
    SamplingFrequency = property(getSamplingFrequency, setSamplingFrequency)

    @security.protected(permissions.View)
    def getRawSampleTypes(self):
        accessor = self.accessor("sample_types", raw=True)
        return accessor(self) or []

    @security.protected(permissions.View)
    def getSampleTypes(self):
        accessor = self.accessor("sample_types")
        return accessor(self) or []

    @security.protected(permissions.ModifyPortalContent)
    def setSampleTypes(self, value):
        mutator = self.mutator("sample_types")
        mutator(self, value)

    @security.protected(permissions.View)
    def getComposite(self):
        accessor = self.accessor("composite")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setComposite(self, value):
        mutator = self.mutator("composite")
        mutator(self, value)

    # BBB: AT schema field property
    Composite = property(getComposite, setComposite)

    @security.protected(permissions.View)
    def getAttachmentFile(self):
        accessor = self.accessor("attachment_file")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAttachmentFile(self, value):
        mutator = self.mutator("attachment_file")
        mutator(self, value)

    # BBB: AT schema field property
    AttachmentFile = property(getAttachmentFile, setAttachmentFile)
