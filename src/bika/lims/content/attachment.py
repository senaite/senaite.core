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
from bika.lims import bikaMessageFactory as _
from bika.lims import deprecated
from bika.lims import logger
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.fields.uidreferencefield import get_backreferences
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.config import PROJECTNAME
from bika.lims.content.bikaschema import BikaSchema
from bika.lims.content.clientawaremixin import ClientAwareMixin
from bika.lims.interfaces.analysis import IRequestAnalysis
from DateTime import DateTime
from plone.app.blob.field import FileField
from Products.Archetypes.atapi import BaseFolder
from Products.Archetypes.atapi import BooleanField
from Products.Archetypes.atapi import BooleanWidget
from Products.Archetypes.atapi import DateTimeField
from Products.Archetypes.atapi import FileWidget
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import registerType
from senaite.core.browser.widgets.referencewidget import ReferenceWidget
from senaite.core.catalog import SETUP_CATALOG

schema = BikaSchema.copy() + Schema((

    FileField(
        "AttachmentFile",
        widget=FileWidget(
            label=_("Attachment"),
        ),
    ),

    UIDReferenceField(
        "AttachmentType",
        required=0,
        allowed_types=("AttachmentType",),
        widget=ReferenceWidget(
            label=_(
                "label_attachment_type",
                default="Attachment Type"),
            description=_(
                "description_attachment_type",
                default="Select the type of the attachment"),
            catalog=SETUP_CATALOG,
            query={
                "is_active": True,
                "sort_on": "sortable_title",
                "sort_order": "ascending"
            },
        ),
    ),

    BooleanField(
        "RenderInReport",
        default=True,
        widget=BooleanWidget(
            label=_("Render attachment in report"),
            description=_(
                "Only images can be rendered in the report directly"),
            visible=True,
        ),
    ),

    StringField(
        "AttachmentKeys",
        searchable=True,
        widget=StringWidget(
            label=_("Attachment Keys"),
        ),
    ),

    DateTimeField(
        "DateLoaded",
        required=1,
        default_method="current_date",
        widget=DateTimeWidget(
            label=_("Date Loaded"),
        ),
    ),
))

schema["id"].required = False
schema["title"].required = False


class Attachment(BaseFolder, ClientAwareMixin):
    """Attachments are stored per client and can be linked to ARs or Analyses
    """
    security = ClassSecurityInfo()
    schema = schema
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        """Rename with the IDServer
        """
        from senaite.core.idserver import renameAfterCreation
        renameAfterCreation(self)

    @security.public
    def Title(self):
        """Return the ID

        :returns: IDServer generated ID
        """
        return self.getId()

    @security.public
    def getRequestID(self):
        """Return the ID of the linked AR
        """
        ar = self.getRequest()
        if not ar:
            return ""
        return api.get_id(ar)

    @security.public
    def getAttachmentTypeUID(self):
        """Return the UID of the assigned attachment type
        """
        attachment_type = self.getAttachmentType()
        if not attachment_type:
            return ""
        return api.get_uid(attachment_type)

    @security.public
    def getLinkedRequests(self):
        """Lookup linked Analysis Requests

        :returns: sorted list of ARs, where the latest AR comes first
        """
        uids = get_backreferences(self, "AnalysisRequestAttachment")
        # fetch the objects by UID and handle nonexisting UIDs gracefully
        uc = api.get_tool("uid_catalog")
        ars = [api.get_object(brain) for brain in uc(UID=uids)]
        # sort by physical path, so that attachments coming from an AR with a
        # higher "-Rn" suffix get sorted correctly.
        # N.B. the created date is the same, hence we can not use it
        return sorted(ars, key=api.get_path, reverse=True)

    @security.public
    def getLinkedAnalyses(self):
        """Lookup linked Analyses

        :returns: sorted list of ANs, where the latest AN comes first
        """
        # Fetch the linked Analyses UIDs
        uids = get_backreferences(self, "AnalysisAttachment")
        # fetch the objects by UID and handle nonexisting UIDs gracefully
        uc = api.get_tool("uid_catalog")
        ans = [api.get_object(brain) for brain in uc(UID=uids)]
        # sort by physical path, so that attachments coming from an AR with a
        # higher "-Rn" suffix get sorted correctly.
        # N.B. the created date is the same, hence we can not use it
        return sorted(ans, key=api.get_path, reverse=True)

    @security.public
    def getTextTitle(self):
        """Return a title for texts and listings
        """
        request_id = self.getRequestID()
        if not request_id:
            return ""

        analysis = self.getAnalysis()
        if not analysis:
            return request_id

        return "%s - %s" % (request_id, analysis.Title())

    @security.public
    def getRequest(self):
        """Return the primary AR this attachment is linked
        """
        ars = self.getLinkedRequests()

        if len(ars) > 1:
            # Attachment is assigned to more than one Analysis Request.
            # This might happen when the AR was invalidated
            ar_ids = ", ".join(map(api.get_id, ars))
            logger.info("Attachment assigned to more than one AR: [{}]. "
                        "The first AR will be returned".format(ar_ids))

        # return the first AR
        if len(ars) >= 1:
            return ars[0]

        # Check if the attachment is linked to an analysis and try to get the
        # AR from the linked analysis
        analysis = self.getAnalysis()
        if IRequestAnalysis.providedBy(analysis):
            return analysis.getRequest()

        return None

    @security.public
    def getAnalysis(self):
        """Return the primary analysis this attachment is linked
        """
        analysis = None
        ans = self.getLinkedAnalyses()

        if len(ans) > 1:
            # Attachment is assigned to more than one Analysis. This might
            # happen when the AR was invalidated
            an_ids = ", ".join(map(api.get_id, ans))
            logger.info("Attachment assigned to more than one Analysis: [{}]. "
                        "The first Analysis will be returned".format(an_ids))

        if len(ans) >= 1:
            analysis = ans[0]

        return analysis

    @security.public
    def current_date(self):
        """Return current date
        """
        return DateTime()

    @security.public
    def getFilename(self):
        """Returns the filename of the underlying File object
        """
        att_file = self.getAttachmentFile()
        return att_file.filename

    @deprecated(comment="Removed in 3.x", replacement="getRenderInReport")
    def getReportOption(self):
        """BBB: returns "r" if RenderInReport is True, otherwise "i"
        """
        if not self.getRenderInReport():
            return "i"
        return "r"

    @deprecated(comment="Removed in 3.x", replacement="setRenderInReport")
    def setReportOption(self, value):
        """BBB: set RenderInReport to True if the passed in value is "r",
                and for all other values to False
        """
        self.setRenderInReport(value == "r")


registerType(Attachment, PROJECTNAME)
