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

import uuid

from bika.lims import api
from bika.lims.decorators import returns_json
from Products.Five.browser import BrowserView
from senaite.core.z3cform.widgets.multiupload.storage import get_storage


class MultiUploadHandler(BrowserView):
    """Handler for multiupload widget AJAX requests

    This view receives file uploads from the React multiupload widget
    and stores them temporarily in shared ZODB storage, returning a
    unique ID. The actual File/Image objects are created later when the
    form is saved via the event subscriber.
    """

    def __call__(self):
        """Entry point for the file upload"""
        request = self.request
        if request.method != "POST":
            return self.fail("Method not allowed", 405)

        # Try to get the uploaded file, as we don't know the field name
        upload = None
        for key in request.form.keys():
            value = request.form.get(key)
            if hasattr(value, "filename") and hasattr(value, "read"):
                upload = value
                break

        if not upload:
            return self.fail("No file uploaded", 400)

        return self.upload(upload)

    def upload(self, upload):
        """Store the uploaded file temporarily in shared ZODB storage

        Uses cluster-safe ZODB storage instead of SESSION to ensure
        uploads are visible across all ZEO client instances.

        :param upload: The uploaded file object
        :returns: JSON response with upload ID and file info
        """
        # Get filename
        filename = api.safe_unicode(
            getattr(upload, "filename", "unknown"))

        # Get the file data
        data = upload.read()

        # Get the file size
        file_size = len(data)

        # Get content MIME type
        content_type = self.get_content_type(upload)

        # Generate unique upload ID
        # This is stored in a hidden <fieldname>.data field
        # and read later by process_form
        upload_id = str(uuid.uuid4())

        # Store in shared ZODB storage (cluster-safe)
        success = self.store_in_storage(
            upload_id, filename, content_type, data)

        if not success:
            return self.fail("Failed to store file in storage", 500)

        return self.send_json({
            "id": upload_id,
            "filename": filename,
            "content_type": content_type,
            "size": file_size,
            "status": "success"
        })

    def store_in_storage(
            self, upload_id, filename, content_type, data):
        """Store uploaded file data in shared ZODB storage

        Uses the cluster-safe TemporaryUploadStorage which stores
        uploads in portal annotations accessible to all ZEO clients.

        :param upload_id: The unique upload ID
        :param filename: The filename
        :param content_type: The MIME type
        :param data: The file data bytes
        :returns: True if stored successfully, False otherwise
        """
        storage = get_storage()
        return storage.store(upload_id, filename, content_type, data)

    def get_content_type(self, upload):
        """Get the MIME type of the uploaded file

        :param upload: The uploaded file object
        :returns: The content type string
        """
        content_type = None
        headers = getattr(upload, "headers", {})
        content_type = headers.get("content-type")
        return content_type or "application/octet-stream"

    def fail(self, message, status=500):
        """Return a failure response

        :param message: The error message
        :param status: The HTTP status code
        :returns: The JSON error response
        """
        data = {
            "error": message,
            "status": "error"
        }
        return self.send_json(data, status=status)

    @returns_json
    def send_json(self, data, status=200):
        """Return a JSON response with a status code

        :param data: The data to return as JSON
        :param status: The HTTP status code
        :returns: The JSON data
        """
        self.request.response.setStatus(status)
        return data
