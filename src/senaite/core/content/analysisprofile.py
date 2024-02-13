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
from senaite.core.interfaces import IAnalysisProfile
from senaite.core.schema.fields import DataGridRow
from senaite.core.z3cform.widgets.listing.widget import ListingWidgetFactory
from zope import schema
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import implementer
from zope.interface import invariant


class IAnalysisProfileRecord(Interface):
    """Record schema for selected services
    """
    uid = schema.TextLine(title=u"Profile UID")
    hidden = schema.Bool(title=u"Hidden")


class IAnalysisProfileSchema(model.Schema):
    """Schema interface
    """

    model.fieldset(
        "analyses",
        label=_(u"Analyses"),
        fields=[
            "services",
        ]
    )

    model.fieldset(
        "accounting",
        label=_(u"Accounting"),
        fields=[
            "commercial_id",
            "use_analysis_profile_price",
            "analysis_profile_price",
            "analysis_profile_vat",
        ]
    )

    title = schema.TextLine(
        title=u"Title",
        required=False,
    )

    description = schema.Text(
        title=u"Description",
        required=False,
    )

    profile_key = schema.TextLine(
        title=_(
            u"title_analysisprofile_profile_key",
            default=u"Profile Keyword"
        ),
        description=_(
            u"description_analysisprofile_profile_key",
            default=u"Please provide a unique profile keyword"
        ),
        required=False,
    )

    directives.widget("services",
                      ListingWidgetFactory,
                      listing_view="analysisprofiles_widget")
    services = schema.List(
        title=_(
            u"title_analysisprofile_services",
            default=u"Profile Analyses"
        ),
        description=_(
            u"description_analysisprofile_services",
            default=u"Select the included analyses for this profile"
        ),
        value_type=DataGridRow(schema=IAnalysisProfileRecord),
    )

    # Commecrial ID
    commercial_id = schema.TextLine(
        title=_(
            u"title_analysisprofile_commercial_id",
            default=u"Commercial ID"
        ),
        description=_(
            u"description_analysisprofile_commercial_id",
            default=u"Commercial ID used for accounting"
        ),
        required=False,
    )

    use_analysis_profile_price = schema.Bool(
        title=_(
            u"title_analysisprofile_use_profile_price",
            default=u"Use analysis profile price"
        ),
        description=_(
            u"description_analysisprofile_use_profile_price",
            default=u"Use profile price instead of single analyses prices"
        ),
        required=False,
    )

    analysis_profile_price = schema.Decimal(
        title=_(
            u"title_analysisprofile_profile_price",
            default=u"Price (excluding VAT)"
        ),
        description=_(
            u"description_analysisprofile_profile_price",
            default=u"Please provide the price excluding VAT"
        ),
        required=False,
    )

    analysis_profile_vat = schema.Decimal(
        title=_(
            u"title_analysisprofile_profile_vat",
            default=u"VAT %"
        ),
        description=_(
            u"description_analysisprofile_profile_vat",
            default=u"Please provide the VAT in percent that is added to the "
                    u"profile price"
        ),
        required=False,
    )

    @invariant
    def validate_profile_key(data):
        """Checks if the profile keyword is unique
        """
        profile_key = data.profile_key
        context = getattr(data, "__context__", None)
        if context and context.profile_key == profile_key:
            # nothing changed
            return
        query = {
            "portal_type": "AnalysisProfile",
            "profile_key": profile_key,  # TODO: add index
        }
        results = api.search(query, catalog=SETUP_CATALOG)
        if len(results) > 0:
            raise Invalid(_("Profile keyword must be unique"))


@implementer(IAnalysisProfile, IAnalysisProfileSchema, IDeactivable)
class AnalysisProfile(Container):
    """AnalysisProfile
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def getProfileKey(self):
        accessor = self.accessor("profile_key")
        value = accessor(self) or ""
        return value.encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setAnalysisProfileID(self, value):
        mutator = self.mutator("profile_key")
        mutator(self, api.safe_unicode(value))

    @security.protected(permissions.View)
    def getRawServices(self):
        """Return the raw value of the services field

        >>> self.getRawServices()
        [{'uid': '...', 'hidden': False}, {'uid': '...', 'hidden': True}, ...]

        :returns: List of dictionaries containing `uid` and `hidden`
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
        """Set services for the profile

        This method accepts either a list of analysis service objects, a list
        of analysis service UIDs or a list of analysis profile service records
        containing the keys `uid` and `hidden`:

        >>> self.setServices([<AnalysisService at ...>, ...])
        >>> self.setServices(['353e1d9bd45d45dbabc837114a9c41e6', '...', ...])
        >>> self.setServices([{'hidden': False, 'uid': '...'}, ...])

        Raises a TypeError if the value does not match any allowed type.
        """
        if not isinstance(value, list):
            value = [value]
        records = []
        for v in value:
            uid = None
            hidden = False
            if isinstance(v, dict):
                uid = v.get("uid")
                hidden = v.get("hidden", False)
            elif api.is_object(v):
                uid = api.get_uid(v)
            elif api.is_uid(v):
                uid = v
            else:
                raise TypeError(
                    "Expected object, uid or record, got %r" % type(v))
            records.append({"uid": uid, "hidden": hidden})
        mutator = self.mutator("services")
        mutator(self, records)

    @security.protected(permissions.View)
    def getCommercialID(self):
        accessor = self.accessor("commercial_id")
        value = accessor(self) or ""
        return value.encode("utf-8")

    @security.protected(permissions.ModifyPortalContent)
    def setCommercialID(self, value):
        mutator = self.mutator("commercial_id")
        mutator(self, api.safe_unicode(value))

    @security.protected(permissions.View)
    def getUseAnalysisProfilePrice(self):
        accessor = self.accessor("use_analysis_profile_price")
        value = accessor(self)
        return bool(value)

    @security.protected(permissions.ModifyPortalContent)
    def setUseAnalysisProfilePrice(self, value):
        mutator = self.mutator("use_analysis_profile_price")
        mutator(self, bool(value))

    @security.protected(permissions.View)
    def getAnalysisProfilePrice(self):
        accessor = self.accessor("analysis_profile_price")
        value = accessor(self) or ""
        return api.to_float(value, 0.0)

    @security.protected(permissions.ModifyPortalContent)
    def setAnalysisProfilePrice(self, value):
        mutator = self.mutator("analysis_profile_price")
        mutator(self, value)

    @security.protected(permissions.View)
    def getAnalysisProfileVAT(self):
        accessor = self.accessor("analysis_profile_vat")
        value = accessor(self) or ""
        return api.to_float(value, 0.0)

    @security.protected(permissions.ModifyPortalContent)
    def setAnalysisProfileVAT(self, value):
        mutator = self.mutator("analysis_profile_vat")
        mutator(self, value)

    def getAnalysisServiceSettings(self, uid):
        """Returns the hidden seettings for the given service UID
        """
        by_uid = self.get_services_by_uid()
        record = by_uid.get(uid, {"uid": uid, "hidden": False})
        return record

    def get_services_by_uid(self):
        """Return the selected services grouped by UID
        """
        records = {}
        for record in self.services:
            records[record.get("uid")] = record
        return records
