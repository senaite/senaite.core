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
from bika.lims import senaiteMessageFactory as _
from plone.autoform import directives
from plone.namedfile.field import NamedBlobFile
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.catalog import REPORT_CATALOG
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import IResultsReport
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


class IMetadataRow(Interface):
    """Schema for metadata record
    """
    paperformat = TextLineField(
        title=_(u"Paper Format"),
        required=False,
    )
    timestamp = TextLineField(
        title=_(u"Timestamp"),
        required=False,
    )
    orientation = TextLineField(
        title=_(u"Orientation"),
        required=False,
    )
    template = TextLineField(
        title=_(u"Template"),
        required=False,
    )
    contained_requests = TextLineField(
        title=_(u"Contained Requests"),
        required=False,
    )


class ISendLogRow(Interface):
    """Schema for send log record
    """
    actor = TextLineField(
        title=_(u"Actor"),
        required=False,
    )
    actor_fullname = TextLineField(
        title=_(u"Actor Fullname"),
        required=False,
    )
    email_send_date = schema.Datetime(
        title=_(u"Email Send Date"),
        required=False,
    )
    email_recipients = TextLineField(
        title=_(u"Email Recipients"),
        required=False,
    )
    email_responsibles = TextLineField(
        title=_(u"Email Responsibles"),
        required=False,
    )
    email_subject = TextLineField(
        title=_(u"Email Subject"),
        required=False,
    )
    email_body = schema.Text(
        title=_(u"Email Body"),
        required=False,
    )
    email_attachments = TextLineField(
        title=_(u"Email Attachments"),
        required=False,
    )


class IRecipientsRow(Interface):
    """Schema for recipients record
    """
    UID = TextLineField(
        title=_(u"UID"),
        required=False,
    )
    Username = TextLineField(
        title=_(u"Username"),
        required=False,
    )
    Fullname = TextLineField(
        title=_(u"Fullname"),
        required=False,
    )
    EmailAddress = TextLineField(
        title=_(u"Email Address"),
        required=False,
    )
    PublicationModes = TextLineField(
        title=_(u"Publication Modes"),
        required=False,
    )


class IResultsReportSchema(model.Schema):
    """Results Report Schema
    """

    # Basic fields
    model.fieldset(
        "default",
        label=_(u"Results Report"),
        fields=[
            "analysis_request",
            "html",
            "pdf",
            "date_printed",
        ]
    )

    directives.widget(
        "analysis_request",
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
    analysis_request = UIDReferenceField(
        title=_(
            u"label_resultsreport_sample",
            default=u"Primary Sample"),
        description=_(
            u"description_resultsreport_sample",
            default=u"The primary sample of the PDF"),
        allowed_types=("AnalysisRequest",),
        multi_valued=False,
        required=True,
    )

    directives.widget(
        "contained_analysis_requests",
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
    contained_analysis_requests = UIDReferenceField(
        title=_(
            u"label_resultsreport_contained_samples",
            default=u"Contained Samples"),
        description=_(
            u"description_resultsreport_contained_samples",
            default=u"Contained samples in the PDF"),
        allowed_types=("AnalysisRequest",),
        multi_valued=True,
        required=False,
    )

    html = schema.Text(
        title=_(u"HTML"),
        description=_(u"HTML content of the report"),
        required=False,
    )

    pdf = NamedBlobFile(
        title=_(u"PDF"),
        description=_(u"PDF file of the report"),
        required=False,
    )

    directives.widget(
        "date_printed",
        DatetimeWidgetFactory,
    )
    date_printed = schema.Datetime(
        title=_(u"Date Printed"),
        description=_(u"Date when the report was printed"),
        required=False,
    )

    # Advanced fields
    model.fieldset(
        "metadata",
        label=_(u"Metadata"),
        fields=[
            "contained_analysis_requests",
            "metadata",
            "recipients",
            "send_log",
        ]
    )

    directives.widget(
        "metadata",
        DataGridWidgetFactory,
    )
    metadata = DataGridField(
        title=_(u"Metadata"),
        description=_(u"Report metadata"),
        value_type=DataGridRow(
            title=_(u"Metadata"),
            schema=IMetadataRow
        ),
        required=False,
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
    )


@implementer(IResultsReport, IResultsReportSchema)
class ResultsReport(Container):
    """A results report for analysis requests, containing the report itself
       in pdf and html format. It includes information about the date when it
       was published, from whom, the report recipients (and their emails) and
       the publication mode
    """
    # Catalogs where this type will be catalogued
    _catalogs = [REPORT_CATALOG]

    security = ClassSecurityInfo()

    @security.protected(permissions.View)
    def Title(self):
        """Return the title of the report
        """
        # Use the primary sample ID as the title
        ar = self.getAnalysisRequest()
        if ar:
            return ar.Title()
        return self.getId()

    def getAnalysisRequest(self):
        """Get the primary analysis request object
        """
        accessor = self.accessor("analysis_request")
        return accessor(self)

    def getContainedAnalysisRequests(self):
        """Get the contained analysis request objects
        """
        accessor = self.accessor("contained_analysis_requests")
        return accessor(self)

    def getClient(self):
        """Get the client from the primary analysis request
        """
        ar = self.getAnalysisRequest()
        if ar:
            return ar.getClient()
        return None

    @security.protected(permissions.View)
    def getMetadata(self):
        """Get metadata as plain dict

        Internally stored as DataGridField (list of dicts), but returns the
        first dict for backward compatibility with senaite.impress and AT.
        """
        accessor = self.accessor("metadata")
        metadata_list = accessor(self) or []
        if metadata_list and len(metadata_list) > 0:
            return metadata_list[0]
        return {}

    @security.protected(permissions.ModifyPortalContent)
    def setMetadata(self, value):
        """Set metadata from plain dict

        Internally stores as DataGridField (list of dicts), but accepts a
        plain dict for backward compatibility with senaite.impress and AT.
        """
        mutator = self.mutator("metadata")
        if value:
            # Wrap dict in list for DataGridField storage
            metadata_list = [value] if isinstance(value, dict) else []
            mutator(self, metadata_list)
        else:
            mutator(self, [])

    # AT-style getters/setters for backward compatibility

    @security.protected(permissions.View)
    def getRawAnalysisRequest(self):
        accessor = self.accessor("analysis_request", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getAnalysisRequestUID(self):
        """Get the UID of the primary analysis request
        """
        return self.getRawAnalysisRequest()

    @security.protected(permissions.ModifyPortalContent)
    def setAnalysisRequest(self, value):
        mutator = self.mutator("analysis_request")
        mutator(self, value)

    # BBB: AT schema field property
    AnalysisRequest = property(getAnalysisRequest, setAnalysisRequest)

    @security.protected(permissions.View)
    def getRawContainedAnalysisRequests(self):
        accessor = self.accessor("contained_analysis_requests", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getContainedAnalysisRequestUIDs(self):
        """Get the UIDs of the contained analysis requests
        """
        return self.getRawContainedAnalysisRequests()

    @security.protected(permissions.ModifyPortalContent)
    def setContainedAnalysisRequests(self, value):
        mutator = self.mutator("contained_analysis_requests")
        mutator(self, value)

    # BBB: AT schema field property
    ContainedAnalysisRequests = property(
        getContainedAnalysisRequests,
        setContainedAnalysisRequests
    )

    @security.protected(permissions.View)
    def getRawHtml(self):
        accessor = self.accessor("html", raw=True)
        return accessor(self)

    @security.protected(permissions.View)
    def getHtml(self):
        accessor = self.accessor("html")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setHtml(self, value):
        mutator = self.mutator("html")
        mutator(self, value)

    # BBB: AT schema field property
    Html = property(getHtml, setHtml)

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
        mutator = self.mutator("pdf")
        mutator(self, value)

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
