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
from bika.lims import senaiteMessageFactory as _
from plone.autoform import directives
from zope.deprecation import deprecate
from plone.namedfile.field import NamedBlobFile as NamedBlobFileField
from plone.namedfile.file import NamedBlobFile
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.catalog import REPORT_CATALOG
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.content.base import Container
from senaite.core.content.mixins import ClientAwareMixin
from senaite.core.interfaces import IResultsReport
from senaite.core.schema import DatetimeField
from senaite.core.schema import UIDReferenceField
from senaite.core.schema.fields import DataGridField
from senaite.core.schema.fields import DataGridRow
from senaite.core.schema.textlinefield import TextLineField
from senaite.core.z3cform.widgets.datagrid import DataGridWidgetFactory
from senaite.core.z3cform.widgets.datetimewidget import DatetimeWidgetFactory
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from zope import schema
from zope.interface import Interface
from zope.interface import implementer


class ISendLogRow(Interface):
    """Schema for send log record
    """
    actor = TextLineField(
        title=_(u"Actor"),
        required=False,
        default=u"",
    )
    actor_fullname = TextLineField(
        title=_(u"Actor Fullname"),
        required=False,
        default=u"",
    )
    email_send_date = DatetimeField(
        title=_(u"Email Send Date"),
        required=False,
        default=None,
    )
    email_recipients = schema.List(
        title=_(u"Email Recipients"),
        value_type=TextLineField(),
        required=False,
        default=[],
    )
    email_responsibles = schema.List(
        title=_(u"Email Responsibles"),
        value_type=TextLineField(),
        required=False,
        default=[],
    )
    email_subject = TextLineField(
        title=_(u"Email Subject"),
        required=False,
        default=u"",
    )
    email_body = schema.Text(
        title=_(u"Email Body"),
        required=False,
        default=u"",
    )
    email_attachments = schema.List(
        title=_(u"Email Attachments"),
        value_type=TextLineField(),
        required=False,
        default=[],
    )


class IRecipientsRow(Interface):
    """Schema for recipients record
    """
    UID = TextLineField(
        title=_(u"UID"),
        required=False,
        default=u"",
    )
    Username = TextLineField(
        title=_(u"Username"),
        required=False,
        default=u"",
    )
    Fullname = TextLineField(
        title=_(u"Fullname"),
        required=False,
        default=u"",
    )
    EmailAddress = TextLineField(
        title=_(u"Email Address"),
        required=False,
        default=u"",
    )
    PublicationModes = TextLineField(
        title=_(u"Publication Modes"),
        required=False,
        default=u"",
    )


class IResultsReportSchema(model.Schema):
    """Results Report Schema
    """

    # Basic fields
    model.fieldset(
        "default",
        label=_(u"Results Report"),
        fields=[
            "sample",
            "pdf",
            "date_printed",
        ]
    )

    directives.widget(
        "sample",
        UIDReferenceWidgetFactory,
        catalog=SAMPLE_CATALOG,
        query={
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending"
        },
        columns=[
            {"name": "Title", "label": _("Sample")},
            {"name": "getClientTitle", "label": _("Client")},
        ],
    )
    sample = UIDReferenceField(
        title=_(
            u"label_resultsreport_sample",
            default=u"Primary Sample"),
        description=_(
            u"description_resultsreport_sample",
            default=u"The primary sample of the PDF"),
        allowed_types=("AnalysisRequest",),
        relationship="ResultsReport.sample",
        multi_valued=False,
        required=True,
        default=None,
    )

    directives.widget(
        "contained_samples",
        UIDReferenceWidgetFactory,
        catalog=SAMPLE_CATALOG,
        query={
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending"
        },
        columns=[
            {"name": "Title", "label": _("Sample")},
            {"name": "getClientTitle", "label": _("Client")},
        ],
    )
    contained_samples = UIDReferenceField(
        title=_(
            u"label_resultsreport_contained_samples",
            default=u"Contained Samples"),
        description=_(
            u"description_resultsreport_contained_samples",
            default=u"Contained samples in the PDF"),
        allowed_types=("AnalysisRequest",),
        relationship="ResultsReport.contained_samples",
        multi_valued=True,
        required=False,
        default=[],
    )

    pdf = NamedBlobFileField(
        title=_(u"PDF"),
        description=_(u"PDF file of the report"),
        required=False,
        default=None,
    )

    directives.widget(
        "date_printed",
        DatetimeWidgetFactory,
    )
    date_printed = DatetimeField(
        title=_(u"Date Printed"),
        description=_(u"Date when the report was printed"),
        required=False,
        default=None,
    )

    # Advanced fields
    model.fieldset(
        "metadata",
        label=_(u"Metadata"),
        fields=[
            "contained_samples",
            "metadata",
            "recipients",
            "send_log",
        ]
    )

    directives.mode(metadata="display")
    metadata = schema.Dict(
        title=_(u"Metadata"),
        description=_(u"Report metadata"),
        key_type=TextLineField(),
        value_type=TextLineField(),
        required=False,
        default={},
    )

    directives.widget(
        "recipients",
        DataGridWidgetFactory,
    )
    recipients = DataGridField(
        title=_(u"Recipients"),
        description=_(u"Report recipients"),
        value_type=DataGridRow(
            title=_(u"Recipient"),
            schema=IRecipientsRow
        ),
        required=False,
        default=[],
    )

    directives.widget(
        "send_log",
        DataGridWidgetFactory,
    )
    send_log = DataGridField(
        title=_(u"Send Log"),
        description=_(u"Email send log"),
        value_type=DataGridRow(
            title=_(u"Send Log Entry"),
            schema=ISendLogRow
        ),
        required=False,
        default=[],
    )


@implementer(IResultsReport, IResultsReportSchema)
class ResultsReport(Container, ClientAwareMixin):
    """A results report for analysis requests, containing the report itself in
       pdf format. It includes information about the date when it was
       published, from whom, the report recipients (and their emails) and the
       publication mode

    Extends `ClientAwareMixin` so the report carries the
    `IClientAwareMixin` marker. Without it, the catalog
    `allowedRolesAndUsers` indexer never appended the
    `client:<uid>` token to the report's `senaite_catalog_report`
    entry, and the per-client `ReportsListingView` query (filtered
    via `BaseCatalog._listAllowedRolesAndUsers`) returned zero
    rows for the client contact.
    """
    # Catalogs where this type will be catalogued
    _catalogs = [REPORT_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def Title(self):
        """Return the title of the report
        """
        # Use the primary sample ID as the title
        sample = self.getSample()
        if sample:
            return sample.Title()
        return self.getId()

    def getSample(self):
        """Get the primary sample object
        """
        accessor = self.accessor("sample")
        return accessor(self)

    def getContainedSamples(self):
        """Get the contained sample objects
        """
        accessor = self.accessor("contained_samples")
        return accessor(self)

    @security.protected(permissions.View)
    def getRawSample(self):
        accessor = self.accessor("sample", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getSampleUID(self):
        """Get the UID of the primary sample
        """
        return self.getRawSample()

    @security.protected(permissions.ModifyPortalContent)
    def setSample(self, value):
        mutator = self.mutator("sample")
        mutator(self, value)

    # BBB: AT schema field property
    Sample = property(getSample, setSample)

    @security.protected(permissions.View)
    def getRawContainedSamples(self):
        accessor = self.accessor("contained_samples", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getContainedSampleUIDs(self):
        """Get the UIDs of the contained samples
        """
        return self.getRawContainedSamples()

    @security.protected(permissions.ModifyPortalContent)
    def setContainedSamples(self, value):
        mutator = self.mutator("contained_samples")
        mutator(self, value)

    # BBB: AT schema field property
    ContainedSamples = property(
        getContainedSamples,
        setContainedSamples
    )

    # BBB: Deprecated methods with old field names
    @deprecate("Use getSample() instead. "
               "Will be removed in SENAITE 3.0")
    def getAnalysisRequest(self):
        """Get the primary analysis request object
        """
        return self.getSample()

    @deprecate("Use getContainedSamples() instead. "
               "Will be removed in SENAITE 3.0")
    def getContainedAnalysisRequests(self):
        """Get the contained analysis request objects
        """
        return self.getContainedSamples()

    def getClient(self):
        """Get the client from the primary sample
        """
        sample = self.getSample()
        if sample:
            return sample.getClient()
        return None

    @security.protected(permissions.View)
    def getMetadata(self):
        """Get metadata as plain dict
        """
        accessor = self.accessor("metadata")
        return accessor(self) or {}

    @security.protected(permissions.ModifyPortalContent)
    def setMetadata(self, value):
        """Set metadata from plain dict
        """
        mutator = self.mutator("metadata")
        mutator(self, value if value else {})

    # AT-style getters/setters for backward compatibility

    @deprecate("Use getRawSample() instead. "
               "Will be removed in SENAITE 3.0")
    @security.protected(permissions.View)
    def getRawAnalysisRequest(self):
        return self.getRawSample()

    @deprecate("Use getSampleUID() instead. "
               "Will be removed in SENAITE 3.0")
    @security.protected(permissions.View)
    def getAnalysisRequestUID(self):
        """Get the UID of the primary analysis request
        """
        return self.getSampleUID()

    @deprecate("Use setSample() instead. "
               "Will be removed in SENAITE 3.0")
    @security.protected(permissions.ModifyPortalContent)
    def setAnalysisRequest(self, value):
        return self.setSample(value)

    # BBB: AT schema field property
    AnalysisRequest = property(getAnalysisRequest, setAnalysisRequest)

    @deprecate("Use getRawContainedSamples() instead. "
               "Will be removed in SENAITE 3.0")
    @security.protected(permissions.View)
    def getRawContainedAnalysisRequests(self):
        return self.getRawContainedSamples()

    @deprecate("Use getContainedSampleUIDs() instead. "
               "Will be removed in SENAITE 3.0")
    @security.protected(permissions.View)
    def getContainedAnalysisRequestUIDs(self):
        """Get the UIDs of the contained analysis requests
        """
        return self.getContainedSampleUIDs()

    @deprecate("Use setContainedSamples() instead. "
               "Will be removed in SENAITE 3.0")
    @security.protected(permissions.ModifyPortalContent)
    def setContainedAnalysisRequests(self, value):
        return self.setContainedSamples(value)

    # BBB: AT schema field property
    ContainedAnalysisRequests = property(
        getContainedAnalysisRequests,
        setContainedAnalysisRequests
    )

    @security.protected(permissions.View)
    def getRawPdf(self):
        accessor = self.accessor("pdf", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getPdf(self):
        accessor = self.accessor("pdf")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setPdf(self, value):
        """Set PDF content

        Accepts:
        - NamedBlobFile instance (used as-is)
        - Raw binary data (auto-converts to NamedBlobFile with default name)
        - Dict with 'data', 'filename', 'contentType' keys
        """
        mutator = self.mutator("pdf")

        if value is None:
            mutator(self, None)
            return

        # If already a NamedBlobFile, use as-is
        if isinstance(value, NamedBlobFile):
            mutator(self, value)
            return

        # If it's a dict, extract components
        if isinstance(value, dict):
            data = value.get("data")
            filename = value.get("filename", u"report.pdf")
            content_type = value.get("contentType", "application/pdf")
        # If it's raw bytes/string, use defaults
        elif isinstance(value, (bytes, str)):
            data = value
            filename = u"report.pdf"
            content_type = "application/pdf"
        else:
            raise ValueError(
                "PDF value must be NamedBlobFile, bytes, or dict")

        # Create NamedBlobFile instance
        pdf_blob = NamedBlobFile(
            data=data,
            filename=api.safe_unicode(filename),
            contentType=content_type
        )

        mutator(self, pdf_blob)

    # BBB: AT schema field property
    Pdf = property(getPdf, setPdf)

    @security.protected(permissions.View)
    def getRawDatePrinted(self):
        accessor = self.accessor("date_printed", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getDatePrinted(self):
        accessor = self.accessor("date_printed")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setDatePrinted(self, value):
        mutator = self.mutator("date_printed")
        mutator(self, value)

    # BBB: AT schema field property
    DatePrinted = property(getDatePrinted, setDatePrinted)

    @security.protected(permissions.View)
    def getRawMetadata(self):
        """Get raw metadata (list of dicts from DataGridField)

        Returns the internal list storage directly, without the dict
        conversion that getMetadata() provides.
        """
        return self.metadata

    # BBB: AT schema field property
    # Note: getMetadata/setMetadata are defined above with dict<->list conversion
    Metadata = property(getMetadata, setMetadata)

    @security.protected(permissions.View)
    def getRawRecipients(self):
        accessor = self.accessor("recipients", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getRecipients(self):
        accessor = self.accessor("recipients")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setRecipients(self, value):
        mutator = self.mutator("recipients")
        mutator(self, value)

    # BBB: AT schema field property
    Recipients = property(getRecipients, setRecipients)

    @security.protected(permissions.View)
    def getRawSendLog(self):
        accessor = self.accessor("send_log", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getSendLog(self):
        accessor = self.accessor("send_log")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSendLog(self, value):
        mutator = self.mutator("send_log")
        mutator(self, value)

    # BBB: AT schema field property
    SendLog = property(getSendLog, setSendLog)


# BBB: Backward compatibility alias
ARReport = ResultsReport
