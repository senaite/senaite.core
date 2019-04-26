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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

import re
import base64

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.permissions import FieldEditResultsInterpretation
from plone import protect
from plone.app.textfield import RichTextValue
from Products.Archetypes.event import ObjectEditedEvent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import event

IMG_DATA_RX = re.compile(r'<img alt="" src="(data:image/.*;base64,)(.*?)" />')


class ARResultsInterpretationView(BrowserView):
    """ Renders the view for ResultsInterpration per Department
    """
    template = ViewPageTemplateFile(
        "templates/analysisrequest_results_interpretation.pt")

    def __init__(self, context, request, **kwargs):
        super(ARResultsInterpretationView, self).__init__(context, request)
        self.request = request
        self.context = context

    def __call__(self):
        if self.request.form.get("submitted", False):
            return self.handle_form_submit()
        return self.template()

    def handle_form_submit(self):
        """Handle form submission
        """
        protect.CheckAuthenticator(self.request)
        logger.info("Handle ResultsInterpration Submit")
        # Save the results interpretation
        res = self.get_resultinterpretations()
        self.context.setResultsInterpretationDepts(res)
        self.add_status_message(_("Changes Saved"), level="info")
        # reindex the object after save to update all catalog metadata
        self.context.reindexObject()
        # notify object edited event
        event.notify(ObjectEditedEvent(self.context))
        return self.request.response.redirect(api.get_url(self.context))

    def get_resultinterpretations(self):
        """Return the result interpretations for each department
        """
        out = []
        items = self.request.form.get("ResultsInterpretationDepts", [])
        for item in items:
            # Handle inline images in the HTML
            richtext = self.convert_inline_images(item.get("richtext", ""))
            # N.B. we get here a ZPublisher record. Converting to dict ensures
            #      we can set values as well.
            data = dict(item)
            data["richtext"] = richtext
            out.append(data)
        return out

    def convert_inline_images(self, html):
        """Converts inline images in the HTML to attachments

        Inline images can be added by FireFox and look like this in HTML:
        <img alt="" src="data:image/png;base64,<BASE64_ENCODED_IMAGE>"/>

        Also see: https://github.com/senaite/senaite.core/issues/1333
        """
        images = re.findall(IMG_DATA_RX, html)
        if images:
            count = len(images)
            # found inline images, convert to Attachments
            logger.info("Converting {} inline images to attachments for {}"
                        .format(count, api.get_path(self.context)))
            for group in images:
                data_type = group[0]
                data = group[1]
                filedata = base64.decodestring(data)
                filename = _("Results Interpretation")
                attachment = self.add_attachment(filedata, filename)
                # remove the image data base64 prefix
                html = html.replace(data_type, "", 1)
                # remove the base64 image data with the attachment URL
                html = html.replace(data, "{}/AttachmentFile".format(
                    attachment.absolute_url()))
            self.add_status_message(
                _("Converted {} inline image(s) to attachment files".
                  format(count)), level="info")
        return html

    def add_attachment(self, filedata, filename=""):
        """Add a new attachment
        """
        # Add a new Attachment
        client = self.context.getClient()
        attachment = api.create(client, "Attachment")
        # Ignore in report
        attachment.setReportOption("i")
        attachment.setAttachmentFile(filedata)
        fileobj = attachment.getAttachmentFile()
        fileobj.filename = filename
        self.context.addAttachment(attachment)
        attachment.processForm()
        self.context.reindexObject()
        return attachment

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    def is_edit_allowed(self):
        """Check if edit is allowed
        """
        checkPermission = self.context.portal_membership.checkPermission
        return checkPermission(FieldEditResultsInterpretation, self.context)

    def get_text(self, department, mode="raw"):
        """Returns the text saved for the selected department
        """
        row = self.context.getResultsInterpretationByDepartment(department)
        rt = RichTextValue(row.get("richtext", ""), "text/plain", "text/html")
        if mode == "output":
            return rt.output
        return rt.raw
