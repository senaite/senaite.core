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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.


from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.interfaces import IDeactivable
from plone.supermodel import model
from plone.autoform import directives
from Products.CMFCore import permissions
from Products.CMFPlone.utils import safe_unicode
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.content.base import Container
from senaite.core.content.mixins import ClientAwareMixin
from senaite.core.interfaces import IAnalysisSpec
from senaite.core.schema import UIDReferenceField
from senaite.core.schema.fields import DataGridRow
from senaite.core.z3cform.widgets.listing.widget import ListingWidgetFactory
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from zope import schema
from zope.i18n import translate
from zope.interface import Interface
from zope.interface import implementer


class IResultsRangeRecord(Interface):
    """Schema for a single row in the ResultsRange datagrid
    """
    uid = schema.TextLine(
        title=_(
            u"label_resultsrange_uid",
            default=u"UID"
        ),
        required=False,
    )
    directives.widget("warn_min", klass=u"numeric")
    warn_min = schema.TextLine(
        title=_(u"label_resultsrange_warn_min", default=u"Min warn"),
        required=False,
        default=u"",
    )
    directives.widget("min", klass=u"numeric")
    min = schema.TextLine(
        title=_(u"label_resultsrange_min", default=u"Min"),
        required=False,
        default=u"",
    )
    min_operator = schema.TextLine(
        title=_(
            u"label_resultsrange_min_operator",
            default=u"Min operator"
        ),
        required=False,
        default=u"geq",
    )
    directives.widget("max", klass=u"numeric")
    max = schema.TextLine(
        title=_(u"label_resultsrange_max", default=u"Max"),
        required=False,
        default=u"",
    )
    directives.widget("warn_max", klass=u"numeric")
    warn_max = schema.TextLine(
        title=_(u"label_resultsrange_warn_max", default=u"Max warn"),
        required=False,
        default=u"",
    )
    max_operator = schema.TextLine(
        title=_(
            u"label_resultsrange_max_operator",
            default=u"Max operator"),
        required=False,
        default=u"leq",
    )
    directives.widget("hidemin", klass=u"numeric")
    hidemin = schema.TextLine(
        title=_(u"label_resultsrange_hidemin", default=u"< Min"),
        required=False,
        default=u"",
    )
    directives.widget("hidemax", klass=u"numeric")
    hidemax = schema.TextLine(
        title=_(u"label_resultsrange_hidemax", default=u"> Max"),
        required=False,
        default=u"",
    )
    rangecomment = schema.TextLine(
        title=_(u"label_resultsrange_rangecomment",
                default=u"Out of range comment"),
        required=False,
        default=u"",
    )

class IAnalysisSpecSchema(model.Schema):
    """Analysis Specification Schema"""

    directives.widget(
        "sample_type",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "portal_type": "SampleType",
            "is_active": True,
            "sort_on": "title",
            "sort_order": "ascending",
        },
        limit=5,
    )
    sample_type = UIDReferenceField(
        title=_(
            u"label_analysisspec_sampletype",
            default=u"Sample Type"
        ),
        description=_(
            u"description_analysisspec_sampletype",
            default=u"Select the sample type for this specification"
        ),
        allowed_types=("SampleType", ),
        multi_valued=False,
        required=True,
    )


    directives.widget(
        "dynamic_analysis_spec",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={
            "portal_type": "DynamicAnalysisSpec",
            "is_active": True,
            "sort_on": "title",
            "sort_order": "ascending",
        },
        limit=5,
    )
    dynamic_analysis_spec = UIDReferenceField(
        title=_(
            u"label_analysisspec_dynamicspec",
            default=u"Dynamic Analysis Specification"
        ),
        description=_(
            u"description_analysisspec_dynamicspec",
            default=u"Link dynamic analysis specification"
        ),
        allowed_types=("DynamicAnalysisSpec", ),
        multi_valued=False,
        required=False,
    )

    title = schema.TextLine(
        title=_(
            "title_containertype_title",
            default="Name"
        ),
        required=True,
    )

    description = schema.Text(
        title=_(
            "title_containertype_description",
            default="Description"
        ),
        required=False,
    )

    directives.widget("results_range",
                      ListingWidgetFactory,
                      listing_view="analysisspec_services_widget")
    results_range = schema.List(
        title=_(
            u"title_analysisspec_results_range",
            default=u"Specifications"
        ),
        description=_(
            u"description_analysisspec_results_range",
            default=u"'Min' and 'Max' values indicate a valid results "
                    u"range. Any result outside this results range will "
                    u"raise an alert.<br/>"
                    u"'Min warn' and 'Max warn' values indicate a "
                    u"shoulder range. Any result outside the results "
                    u"range but within the shoulder range will raise a "
                    u"less severe alert.<br/>"
                    u"If the result is out of range, the value set for "
                    u"'&lt; Min' or '&gt; Max' will be displayed in lists "
                    u"and results reports instead of the real result. In "
                    u"such case, the value set for 'Out of range comment' "
                    u"will be displayed in results report as well"
        ),
        value_type=DataGridRow(schema=IResultsRangeRecord),
        default=[],
        required=True,
    )


@implementer(IAnalysisSpec, IAnalysisSpecSchema, IDeactivable)
class AnalysisSpec(Container, ClientAwareMixin):
    """Analysis Specification content type
    """
    _catalogs = [SETUP_CATALOG]
    security = ClassSecurityInfo()

    def Title(self):
        title = self.title or self.getSampleTypeTitle() or ""
        return safe_unicode(title).encode("utf-8")

    @security.protected(permissions.View)
    def contextual_title(self):
        """Returns the title with the context (Lab or Client)
        """
        parent = api.get_parent(self)
        portal_type = api.get_portal_type(parent)
        if portal_type == "Client":
            context = translate(_(u"Client"))
        else:
            context = translate(_(u"Lab"))
        return u"{} ({})".format(safe_unicode(self.title), context)

    @security.protected(permissions.View)
    def getResultsRange(self):
        return self.getRawServices()

    @security.protected(permissions.ModifyPortalContent)
    def setResultsRange(self, value, keep_inactive=True):
        return self.setServices(value, keep_inactive)

    ResultsRange = property(getResultsRange, setResultsRange)

    @security.protected(permissions.View)
    def getRawSampleType(self):
        accessor = self.accessor("sample_type", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getSampleType(self):
        accessor = self.accessor("sample_type")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSampleType(self, value):
        mutator = self.mutator("sample_type")
        mutator(self, value)

    @security.protected(permissions.View)
    def getSampleTypeUID(self):
        return self.getRawSampleType()

    SampleType = property(getSampleType, setSampleType)

    @security.protected(permissions.View)
    def getSampleTypeTitle(self):
        st = self.getSampleType()
        return api.get_title(st)

    @security.protected(permissions.View)
    def getRawDynamicAnalysisSpec(self):
        accessor = self.accessor("dynamic_analysis_spec", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getDynamicAnalysisSpec(self):
        accessor = self.accessor("dynamic_analysis_spec")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setDynamicAnalysisSpec(self, value):
        mutator = self.mutator("dynamic_analysis_spec")
        mutator(self, value)

    DynamicAnalysisSpec = property(getDynamicAnalysisSpec, setDynamicAnalysisSpec)

    @security.protected(permissions.View)
    def getRawServices(self):
        """Return the raw value of the services field
        """
        accessor = self.accessor("results_range")
        services = accessor(self)
        if services:
            return [s.get("uid") for s in services]
        return []

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
        """Set services for the analysis specification
        """
        if not isinstance(value, (list, dict)):
            raise TypeError(
                "Expected a dict or list, got %r" % type(value))
        if isinstance(value, dict):
            value = [value]

        records = []
        for v in value:
            if api.is_object(v):
                uid = api.get_uid(v)
                v = {"uid": uid}
            elif api.is_uid(v):
                uid = v
                v = {"uid": uid}

            uid = v.get("uid", "")
            warn_min = v.get("warn_min", "")
            min_val = v.get("min", "")
            min_operator = v.get("min_operator", "geq")
            max_val = v.get("max", "")
            warn_max = v.get("warn_max", "")
            max_operator = v.get("max_operator", "leq")
            hidemin = v.get("hidemin", "")
            hidemax = v.get("hidemax", "")
            rangecomment = v.get("rangecomment", "")

            if uid:
                uid = api.get_uid(uid)

            records.append({
                "uid": uid,
                "warn_min": warn_min,
                "min": min_val,
                "min_operator": min_operator,
                "max": max_val,
                "warn_max": warn_max,
                "max_operator": max_operator,
                "hidemin": hidemin,
                "hidemax": hidemax,
                "rangecomment": rangecomment,
            })

        if keep_inactive:
            uids = [record.get("uid") for record in records]
            for record in self.getRawServices():
                uid = record.get("uid")
                if uid in uids:
                    continue
                obj = api.get_object(uid)
                if not api.is_active(obj):
                    records.append(record)

        mutator = self.mutator("results_range")
        mutator(self, records)

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
