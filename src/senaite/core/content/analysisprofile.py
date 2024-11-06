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
from senaite.core.content.mixins import ClientAwareMixin
from senaite.core.interfaces import IAnalysisProfile
from senaite.core.schema import UIDReferenceField
from senaite.core.schema.fields import DataGridRow
from senaite.core.z3cform.widgets.listing.widget import ListingWidgetFactory
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
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
        title=_(
            u"title_analysisprofile_title",
            default=u"Name"
        ),
        required=True,
    )

    description = schema.Text(
        title=_(
            u"title_analysisprofile_description",
            default=u"Description"
        ),
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
        default=u""
    )

    directives.widget("services",
                      ListingWidgetFactory,
                      listing_view="analysisprofile_services_widget")
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
        default=[],
        required=True,
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
            u"label_analysisprofile_sampletypes",
            default=u"Sample types"
        ),
        description=_(
            u"description_analysisprofile_sampletypes",
            default=u"Sample types for which this analysis profile is "
                    u"supported. This profile won't be available for "
                    u"selection in sample creation and edit forms unless the "
                    u"selected sample type is one of these. If no sample type "
                    u"is set here, this profile will always be available for "
                    u"selection, regardless of the sample type of the sample."
        ),
        allowed_types=("SampleType", ),
        multi_valued=True,
        required=False,
    )

    @invariant
    def validate_profile_key(data):
        """Checks if the profile keyword is unique
        """
        profile_key = data.profile_key
        if not profile_key:
            # no further checks required
            return
        context = getattr(data, "__context__", None)
        if context and context.profile_key == profile_key:
            # nothing changed
            return
        query = {
            "portal_type": "AnalysisProfile",
            "profile_key": profile_key,
        }
        results = api.search(query, catalog=SETUP_CATALOG)
        if len(results) > 0:
            raise Invalid(_("Profile keyword must be unique"))


@implementer(IAnalysisProfile, IAnalysisProfileSchema, IDeactivable)
class AnalysisProfile(Container, ClientAwareMixin):
    """AnalysisProfile
    """
    # Catalogs where this type will be catalogued
    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def getProfileKey(self):
        accessor = self.accessor("profile_key")
        value = accessor(self) or ""
        return api.to_utf8(value)

    @security.protected(permissions.ModifyPortalContent)
    def setProfileKey(self, value):
        mutator = self.mutator("profile_key")
        mutator(self, api.safe_unicode(value))

    # BBB: AT schema field property
    ProfileKey = property(getProfileKey, setProfileKey)

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
    def getServices(self, active_only=True):
        """Returns a list of service objects

        >>> self.getServices()
        [<AnalysisService at ...>,  <AnalysisService at ...>, ...]

        :returns: List of analysis service objects
        """
        services = map(api.get_object, self.getRawServiceUIDs())
        if active_only:
            # filter out inactive services
            services = filter(api.is_active, services)
        return list(services)

    @security.protected(permissions.ModifyPortalContent)
    def setServices(self, value, keep_inactive=True):
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

        if keep_inactive:
            # keep inactive services so they come up again when reactivated
            uids = [record.get("uid") for record in records]
            for record in self.getRawServices():
                uid = record.get("uid")
                if uid in uids:
                    continue
                obj = api.get_object(uid)
                if not api.is_active(obj):
                    records.append(record)

        mutator = self.mutator("services")
        mutator(self, records)

    # BBB: AT schema field property
    Service = Services = property(getServices, setServices)

    @security.protected(permissions.View)
    def getServiceUIDs(self, active_only=True):
        """Returns a list of UIDs for the referenced AnalysisService objects

        :param active_only: If True, only UIDs of active services are returned
        :returns: A list of unique identifiers (UIDs)
        """
        if active_only:
            services = self.getServices(active_only=active_only)
            return list(map(api.get_uid, services))
        return self.getRawServiceUIDs()

    @security.protected(permissions.View)
    def getRawServiceUIDs(self):
        """Returns the list of UIDs stored as raw data in the 'Services' field

        :returns: A list of UIDs extracted from the raw 'Services' data.
        """
        services = self.getRawServices()
        return list(map(lambda record: record.get("uid"), services))

    @security.protected(permissions.View)
    def getCommercialID(self):
        accessor = self.accessor("commercial_id")
        value = accessor(self) or ""
        return api.to_utf8(value)

    @security.protected(permissions.ModifyPortalContent)
    def setCommercialID(self, value):
        mutator = self.mutator("commercial_id")
        mutator(self, api.safe_unicode(value))

    # BBB: AT schema field property
    CommercialID = property(getCommercialID, setCommercialID)

    @security.protected(permissions.View)
    def getUseAnalysisProfilePrice(self):
        accessor = self.accessor("use_analysis_profile_price")
        value = accessor(self)
        return bool(value)

    @security.protected(permissions.ModifyPortalContent)
    def setUseAnalysisProfilePrice(self, value):
        mutator = self.mutator("use_analysis_profile_price")
        mutator(self, bool(value))

    # BBB: AT schema field property
    UseAnalysisProfilePrice = property(
        getUseAnalysisProfilePrice, setUseAnalysisProfilePrice)

    @security.protected(permissions.View)
    def getAnalysisProfilePrice(self):
        accessor = self.accessor("analysis_profile_price")
        value = accessor(self) or ""
        return api.to_float(value, 0.0)

    @security.protected(permissions.ModifyPortalContent)
    def setAnalysisProfilePrice(self, value):
        mutator = self.mutator("analysis_profile_price")
        mutator(self, value)

    # BBB: AT schema field property
    AnalysisProfilePrice = property(
        getAnalysisProfilePrice, setAnalysisProfilePrice)

    @security.protected(permissions.View)
    def getAnalysisProfileVAT(self):
        accessor = self.accessor("analysis_profile_vat")
        value = accessor(self) or ""
        return api.to_float(value, 0.0)

    @security.protected(permissions.ModifyPortalContent)
    def setAnalysisProfileVAT(self, value):
        mutator = self.mutator("analysis_profile_vat")
        mutator(self, value)

    # BBB: AT schema field property
    AnalysisProfileVAT = property(getAnalysisProfileVAT, setAnalysisProfileVAT)

    @security.protected(permissions.View)
    def getAnalysisServiceSettings(self, uid):
        """Returns the hidden seettings for the given service UID
        """
        uid = api.get_uid(uid)
        by_uid = self.get_services_by_uid()
        record = by_uid.get(uid, {"uid": uid, "hidden": False})
        return record

    @security.protected(permissions.ModifyPortalContent)
    def setAnalysisServicesSettings(self, settings):
        """BBB: Update settings for selected service UIDs

        This method expects a list of dictionaries containing the service `uid`
        and the `hidden` setting.

        This is basically the same format as stored in the `services` field!

        However, we want to just update the settings for selected service UIDs"

        >>> settings =  [{'uid': '...', 'hidden': False}, ...]
        >>> setAnalysisServicesSettings(settings)
        """
        if not isinstance(settings, list):
            settings = [settings]

        by_uid = self.get_services_by_uid()

        for setting in settings:
            if not isinstance(setting, dict):
                raise TypeError(
                    "Expected a record containing `uid` and `hidden`, got %s"
                    % type(setting))
            uid = setting.get("uid")
            hidden = setting.get("hidden", False)

            if not uid:
                raise ValueError("UID is missing in setting %r" % setting)

            record = by_uid.get(uid)
            if not record:
                continue
            record["hidden"] = hidden

        # set back the new services
        self.setServices(by_uid.values())

    @security.protected(permissions.View)
    def getAnalysisServicesSettings(self):
        """BBB: Return hidden settings for selected services

        :returns: List of dictionaries containing `uid` and `hidden` settings
        """
        # Note: We store the selected service UIDs and the hidden setting in
        # the `services` field. Therefore, we can just return the raw value.
        return self.getRawServices()

    # BBB: AT schema (computed) field property
    AnalysisServicesSettings = property(getAnalysisServicesSettings)

    @security.protected(permissions.View)
    def get_services_by_uid(self):
        """Return the selected services grouped by UID
        """
        records = {}
        for record in self.services:
            records[record.get("uid")] = record
        return records

    def isAnalysisServiceHidden(self, service):
        """Check if the service is configured as hidden
        """
        obj = api.get_object(service)
        uid = api.get_uid(service)
        services = self.get_services_by_uid()
        record = services.get(uid)
        if not record:
            return obj.getRawHidden()
        return record.get("hidden", False)

    @security.protected(permissions.View)
    def getPrice(self):
        """Returns the price of the profile, without VAT
        """
        return self.getAnalysisProfilePrice()

    @security.protected(permissions.View)
    def getVATAmount(self):
        """Compute VAT amount
        """
        price = self.getPrice()
        vat = self.getAnalysisProfileVAT()
        return float(price) * float(vat) / 100

    # BBB: AT schema (computed) field property
    VATAmount = property(getVATAmount)

    @security.protected(permissions.View)
    def getTotalPrice(self):
        """Calculate the final price using the VAT and the subtotal price
        """
        price = self.getPrice()
        vat = self.getVATAmount()
        return float(price) + float(vat)

    # BBB: AT schema (computed) field property
    TotalPrice = property(getTotalPrice)

    def remove_service(self, service):
        """Remove the service from the profile

        If the service is not selected in the profile, returns False.

        NOTE: This method is used when an Analysis Service was deactivated.

        :param service: The service to be removed from this profile
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
