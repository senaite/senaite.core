# -*- coding: utf-8 -*-

from bika.lims import api
from Products.Five.browser import BrowserView
from senaite.core import logger


class ResolveAttachmentView(BrowserView):
    """Resolve Attachment by UID

    This view is used for attachment image links to attachments
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        uid = self.request.get("uid")
        attachment = api.get_object_by_uid(uid, default=None)
        if attachment is None:
            logger.error("No attachment found for UID: '{}'".format(uid))
            return
        return self.download(attachment)

    def get_attachment_info(self, attachment):
        """Returns a dictionary of attachment information
        """
        blob = attachment.getAttachmentFile()

        return {
            "data": blob.data,
            "content_type": blob.content_type,
            "filename": blob.filename,
            "last_modified": api.get_modification_date(attachment),
        }

    def download(self, attachment):
        info = self.get_attachment_info(attachment)
        data = info.get("data", "")
        content_type = info.get("content_type", "application/octet-stream")
        last_modified = info.get("last_modified")
        response = self.request.response
        set_header = response.setHeader
        set_header("Content-Type", "{}".format(content_type))
        set_header("Content-Length", len(data))
        set_header("Last-Modified", last_modified)
        response.write(data)
