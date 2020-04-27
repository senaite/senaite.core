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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.browser import BrowserView
from bika.lims.utils import get_image
from plone.memoize import view
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZODB.POSException import POSKeyError


class AnalysisReportInfoView(BrowserView):
    """Show details of the Analysis Report
    """
    template = ViewPageTemplateFile("templates/analysisreport_info.pt")

    def __init__(self, context, request):
        super(AnalysisReportInfoView, self).__init__(context, request)

    def __call__(self):
        # disable the editable border
        self.request.set("disable_border", 1)
        return self.template()

    @view.memoize
    def get_report(self):
        report_uid = self.request.form.get("report_uid")
        return api.get_object_by_uid(report_uid, None)

    @view.memoize
    def get_primary_sample(self):
        report = self.get_report()
        return report.getAnalysisRequest()

    @view.memoize
    def get_metadata(self):
        report = self.get_report()
        return report.getMetadata()

    @view.memoize
    def get_sendlog(self):
        report = self.get_report()
        records = report.getSendLog()
        return list(reversed(records))

    @view.memoize
    def get_contained_samples(self):
        metadata = self.get_metadata()
        samples = metadata.get("contained_requests", [])
        sample_uids = filter(api.is_uid, samples)
        return map(api.get_object_by_uid, sample_uids)

    def get_icon_for(self, typename):
        """Returns the big image icon by its (type-)name
        """
        image = "{}_big.png".format(typename)
        return get_image(
            image, width="20px", style="vertical-align: baseline;")

    def get_filesize(self, f):
        """Return the filesize of the PDF as a float
        """
        try:
            filesize = float(f.get_size())
            return float("%.2f" % (filesize / 1024))
        except (POSKeyError, TypeError, AttributeError):
            return 0.0

    @view.memoize
    def get_attachment_data_by_uid(self, uid):
        """Retrieve attachment data by UID
        """
        attachment = api.get_object_by_uid(uid, default=None)
        # Attachment file not found/deleted
        if attachment is None:
            return {}
        f = attachment.getAttachmentFile()
        attachment_type = attachment.getAttachmentType()
        attachment_keys = attachment.getAttachmentKeys()
        filename = f.filename
        filesize = self.get_filesize(f)
        mimetype = f.getContentType()
        report_option = attachment.getReportOption()

        return {
            "obj": attachment,
            "attachment_type": attachment_type,
            "attachment_keys": attachment_keys,
            "file": f,
            "uid": uid,
            "filesize": filesize,
            "filename": filename,
            "mimetype": mimetype,
            "report_option": report_option,
        }
