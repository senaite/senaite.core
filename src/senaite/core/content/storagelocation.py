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
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import IStorageLocation
from zope import schema
from zope.interface import implementer
from plone.supermodel import model
from Products.CMFCore import permissions


class IStorageLocationSchema(model.Schema):
    """Schema interface
    """

    title = schema.TextLine(
        title=_(
            "title_storagelocation_title",
            default="Address",
        ),
        required=True,
    )

    description = schema.Text(
        title=_(
            "title_storagelocation_description",
            default="Description",
        ),
        required=False,
    )

    site_title = schema.TextLine(
        title=_(
            "title_storagelocation_site_title",
            default="Site Title"
        ),
        description=_(
            "description_storagelocation_site_title",
            default="Title of the site",
        ),
        required=False,
    )

    site_code = schema.TextLine(
        title=_(
            "title_storagelocation_site_code",
            default="Site Code",
        ),
        description=_(
            "description_storagelocation_site_code",
            default="Code for the site",
        ),
        required=False,
    )

    site_description = schema.TextLine(
        title=_(
            "title_storagelocation_site_description",
            default="Site Description",
        ),
        description=_(
            "description_storagelocation_site_description",
            default="Description of the site",
        ),
        required=False,
    )

    location_title = schema.TextLine(
        title=_(
            "title_storagelocation_location_title",
            default="Location Title",
        ),
        description=_(
            "description_storagelocation_location_title",
            default="Title of location",
        ),
        required=False,
    )

    location_code = schema.TextLine(
        title=_(
            "title_storagelocation_location_code",
            default="Location Code",
        ),
        description=_(
            "description_storagelocation_location_code",
            default="Code for the location",
        ),
        required=False,
    )

    location_description = schema.TextLine(
        title=_(
            "title_storagelocation_location_description",
            default="Location Description",
        ),
        description=_(
            "description_storagelocation_location_description",
            default="Description of the location",
        ),
        required=False,
    )

    location_type = schema.TextLine(
        title=_(
            "title_storagelocation_location_type",
            default="Location Type",
        ),
        description=_(
            "description_storagelocation_location_type",
            default="Type of location",
        ),
        required=False,
    )

    shelf_title = schema.TextLine(
        title=_(
            "title_storagelocation_shelf_title",
            default="Shelf Title",
        ),
        description=_(
            "description_storagelocation_shelf_title",
            default="Title of the shelf",
        ),
        required=False,
    )

    shelf_code = schema.TextLine(
        title=_(
            "title_storagelocation_shelf_code",
            default="Shelf Code",
        ),
        description=_(
            "description_storagelocation_shelf_code",
            default="Code the the shelf",
        ),
        required=False,
    )

    shelf_description = schema.TextLine(
        title=_(
            "title_storagelocation_shelf_description",
            default="Shelf Description",
        ),
        description=_(
            "description_storagelocation_shelf_description",
            default="Description of the shelf",
        ),
        required=False,
    )


@implementer(IStorageLocation, IStorageLocationSchema, IDeactivable)
class StorageLocation(Container):
    """Storage Location
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def getSiteTitle(self):
        accessor = self.accessor("site_title")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSiteTitle(self, value):
        mutator = self.mutator("site_title")
        mutator(self, value)

    # BBB: AT schema field property
    SiteTitle = property(getSiteTitle, setSiteTitle)

    @security.protected(permissions.View)
    def getSiteCode(self):
        accessor = self.accessor("site_code")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSiteCode(self, value):
        mutator = self.mutator("site_code")
        mutator(self, value)

    # BBB: AT schema field property
    SiteCode = property(getSiteCode, setSiteCode)

    @security.protected(permissions.View)
    def getSiteDescription(self):
        accessor = self.accessor("site_description")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSiteDescription(self, value):
        mutator = self.mutator("site_description")
        mutator(self, value)

    # BBB: AT schema field property
    SiteDescription = property(getSiteDescription, setSiteDescription)

    @security.protected(permissions.View)
    def getLocationTitle(self):
        accessor = self.accessor("location_title")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setLocationTitle(self, value):
        mutator = self.mutator("location_title")
        mutator(self, value)

    # BBB: AT schema field property
    LocationTitle = property(getLocationTitle, setLocationTitle)

    @security.protected(permissions.View)
    def getLocationCode(self):
        accessor = self.accessor("location_code")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setLocationCode(self, value):
        mutator = self.mutator("location_code")
        mutator(self, value)

    # BBB: AT schema field property
    LocationCode = property(getLocationCode, setLocationCode)

    @security.protected(permissions.View)
    def getLocationDescription(self):
        accessor = self.accessor("location_description")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setLocationDescription(self, value):
        mutator = self.mutator("location_description")
        mutator(self, value)

    # BBB: AT schema field property
    LocationDescription = property(getLocationDescription,
                                   setLocationDescription)

    @security.protected(permissions.View)
    def getLocationType(self):
        accessor = self.accessor("location_type")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setLocationType(self, value):
        mutator = self.mutator("location_type")
        mutator(self, value)

    # BBB: AT schema field property
    LocationType = property(getLocationType, setLocationType)

    @security.protected(permissions.View)
    def getShelfTitle(self):
        accessor = self.accessor("shelf_title")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setShelfTitle(self, value):
        mutator = self.mutator("shelf_title")
        mutator(self, value)

    # BBB: AT schema field property
    ShelfTitle = property(getShelfTitle, setShelfTitle)

    @security.protected(permissions.View)
    def getShelfCode(self):
        accessor = self.accessor("shelf_code")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setShelfCode(self, value):
        mutator = self.mutator("shelf_code")
        mutator(self, value)

    # BBB: AT schema field property
    ShelfCode = property(getShelfCode, setShelfCode)

    @security.protected(permissions.View)
    def getShelfDescription(self):
        accessor = self.accessor("shelf_description")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setShelfDescription(self, value):
        mutator = self.mutator("shelf_description")
        mutator(self, value)

    # BBB: AT schema field property
    ShelfDescription = property(getShelfDescription, setShelfDescription)
