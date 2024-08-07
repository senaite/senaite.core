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
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.widgets import DateTimeWidget
from Products.Archetypes.atapi import TextAreaWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.content.clientawaremixin import ClientAwareMixin
from bika.lims.interfaces import IARReport
from plone.app.blob.field import BlobField
from Products.Archetypes import atapi
from Products.Archetypes.public import BaseFolder
from Products.Archetypes.public import Schema
from Products.Archetypes.public import TextField
from senaite.core.browser.fields.datetime import DateTimeField
from senaite.core.browser.fields.record import RecordField
from senaite.core.browser.fields.records import RecordsField
from senaite.core.browser.widgets.referencewidget import ReferenceWidget
from senaite.core.catalog import SAMPLE_CATALOG
from zope.interface import implements

schema = BikaSchema.copy() + Schema((

    UIDReferenceField(
        "AnalysisRequest",
        allowed_types=("AnalysisRequest",),
        required=1,
        widget=ReferenceWidget(
            label=_(
                "label_arreport_sample",
                default="Primary Sample"),
            description=_(
                "description_arreport_sample",
                default="The primary sample of the PDF"),
            readonly=True,
            visible={
                "view": "visible",
            },
            catalog_name=SAMPLE_CATALOG,
            query={
                "is_active": True,
                "sort_on": "sortable_title",
                "sort_order": "ascending"
            },
            columns=[
                {"name": "Title", "label": _("Sample")},
                {"name": "ClientTitle", "label": _("Client")},
            ],
        )
    ),

    # readonly field
    UIDReferenceField(
        "ContainedAnalysisRequests",
        multiValued=True,
        allowed_types=("AnalysisRequest",),
        relationship="ARReportAnalysisRequest",
        widget=ReferenceWidget(
            label=_(
                "label_arreport_contained_samples",
                default="Contained Samples"),
            description=_(
                "description_arreport_contained_samples",
                default="Contained samples in the PDF"),
            readonly=True,
            visible={
                "view": "visible",
            },
            catalog_name=SAMPLE_CATALOG,
            query={
                "is_active": True,
                "sort_on": "sortable_title",
                "sort_order": "ascending"
            },
            columns=[
                {"name": "Title", "label": _("Sample")},
                {"name": "ClientTitle", "label": _("Client")},
            ],
        )
    ),

    RecordField(
        "Metadata",
        type="metadata",
        subfields=(
            "paperformat",
            "timestamp",
            "orientation",
            "template",
            "contained_requests",
        ),
    ),

    RecordsField(
        "SendLog",
        type="sendlog",
        subfields=(
            "actor",
            "actor_fullname",
            "email_send_date",
            "email_recipients",
            "email_responsibles",
            "email_subject",
            "email_body",
            "email_attachments",
        ),
    ),

    TextField(
        "Html",
        allowable_content_types=("text/html",),
        default_output_type="text/html",
        widget=TextAreaWidget(
            label=_("HTML"),
            cols=30,
            rows=30,
        ),
    ),

    BlobField(
        "Pdf",
        default_content_type="application/pdf",
    ),

    RecordsField(
        "Recipients",
        type="recipients",
        subfields=(
            "UID",
            "Username",
            "Fullname",
            "EmailAddress",
            "PublicationModes"
        ),
    ),

    DateTimeField(
        "DatePrinted",
        mode="rw",
        widget=DateTimeWidget(
            label=_("Date Printed"),
            visible={
                "edit": "visible",
                "view": "visible",
            }
        ),
    ),
))

schema["id"].required = False
schema["title"].required = False


class ARReport(BaseFolder, ClientAwareMixin):
    """An AnalysisRequest report, containing the report itself in pdf and html
       format. It includes information about the date when was published, from
       whom, the report recipients (and their emails) and the publication mode
    """
    implements(IARReport)

    security = ClassSecurityInfo()
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from senaite.core.idserver import renameAfterCreation
        renameAfterCreation(self)


atapi.registerType(ARReport, PROJECTNAME)
