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
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.content.base import Container
from senaite.core.interfaces import IResultsReport
from senaite.core.schema import UIDReferenceField
from senaite.core.schema.fields import DataGridField
from senaite.core.schema.fields import DataGridRow
from senaite.core.z3cform.widgets.datagrid import DataGridWidgetFactory
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from zope import schema
from zope.interface import Interface
from zope.interface import implementer


class IMetadataRow(Interface):
    """Schema for metadata record
    """
    paperformat = schema.TextLine(
        title=_(u"Paper Format"),
        required=False,
    )
    timestamp = schema.Datetime(
        title=_(u"Timestamp"),
        required=False,
    )
    orientation = schema.TextLine(
        title=_(u"Orientation"),
        required=False,
    )
    template = schema.TextLine(
        title=_(u"Template"),
        required=False,
    )
    contained_requests = schema.TextLine(
        title=_(u"Contained Requests"),
        required=False,
    )


class ISendLogRow(Interface):
    """Schema for send log record
    """
    actor = schema.TextLine(
        title=_(u"Actor"),
        required=False,
    )
    actor_fullname = schema.TextLine(
        title=_(u"Actor Fullname"),
        required=False,
    )
    email_send_date = schema.Datetime(
        title=_(u"Email Send Date"),
        required=False,
    )
    email_recipients = schema.TextLine(
        title=_(u"Email Recipients"),
        required=False,
    )
    email_responsibles = schema.TextLine(
        title=_(u"Email Responsibles"),
        required=False,
    )
    email_subject = schema.TextLine(
        title=_(u"Email Subject"),
        required=False,
    )
    email_body = schema.Text(
        title=_(u"Email Body"),
        required=False,
    )
    email_attachments = schema.TextLine(
        title=_(u"Email Attachments"),
        required=False,
    )


class IRecipientsRow(Interface):
    """Schema for recipients record
    """
    UID = schema.TextLine(
        title=_(u"UID"),
        required=False,
    )
    Username = schema.TextLine(
        title=_(u"Username"),
        required=False,
    )
    Fullname = schema.TextLine(
        title=_(u"Fullname"),
        required=False,
    )
    EmailAddress = schema.TextLine(
        title=_(u"Email Address"),
        required=False,
    )
    PublicationModes = schema.TextLine(
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
            "contained_analysis_requests",
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
    _catalogs = []

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
        from bika.lims import api
        uid = getattr(self, "analysis_request", None)
        if not uid:
            return None
        return api.get_object_by_uid(uid)

    def getContainedAnalysisRequests(self):
        """Get the contained analysis request objects
        """
        from bika.lims import api
        uids = getattr(self, "contained_analysis_requests", [])
        if not uids:
            return []
        return [api.get_object_by_uid(uid) for uid in uids if uid]

    def getClient(self):
        """Get the client from the primary analysis request
        """
        ar = self.getAnalysisRequest()
        if ar:
            return ar.getClient()
        return None


# BBB: Keep ARReport as an alias for backward compatibility
ARReport = ResultsReport
