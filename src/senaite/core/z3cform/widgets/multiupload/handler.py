# -*- coding: utf-8 -*-

import uuid

from bika.lims import api
from Products.Five.browser import BrowserView
from bika.lims.decorators import returns_json


class MultiUploadHandler(BrowserView):
    """Handler for multiupload widget AJAX requests

    This view receives file uploads from the React multiupload widget
    and stores them temporarily in the session, returning a unique ID.
    The actual File/Image objects are created later in the widget's
    process_form method.
    """

    def __call__(self):
        """Entry point for the file upload
        """
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
        """Store the uploaded file temporarily in the session

        NOTE: This is required since we might be in the add form.

        :param upload: The uploaded file object
        :returns: JSON response with upload ID and file info
        """
        try:
            # Get filename
            filename = api.safe_unicode(getattr(upload, "filename", "unknown"))

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

            # Store in session
            session = self.request.SESSION
            if "multiupload_files" not in session:
                session["multiupload_files"] = {}

            session["multiupload_files"][upload_id] = {
                "data": data,
                "filename": filename,
                "content_type": content_type,
            }

            api.logger.info(u"Stored upload {} in session for file {}".format(
                upload_id, filename))

            return self.send_json({
                "id": upload_id,
                "filename": filename,
                "content_type": content_type,
                "size": file_size,
                "status": "success"
            })

        except Exception as e:
            api.logger.error("Error handling file upload: {}".format(str(e)))
            return self.fail(str(e), 500)

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
