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
        """
        try:
            # Get filename
            filename = api.safe_unicode(getattr(upload, "filename", "unknown"))

            # Get the file data
            data = upload.read()

            # Get the file size
            file_size = len(data)

            # Get content type
            content_type = self.get_content_type(upload)

            # Determine if it's an image
            is_image = self.is_image(content_type)

            # Generate unique upload ID
            upload_id = str(uuid.uuid4())

            # Store in session
            session = self.request.SESSION
            if "multiupload_files" not in session:
                session["multiupload_files"] = {}

            session["multiupload_files"][upload_id] = {
                "data": data,
                "filename": filename,
                "content_type": content_type,
                "is_image": is_image,
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
        """Get the content type of the uploaded file
        """
        headers = getattr(upload, "headers", {})
        if hasattr(headers, "get"):
            content_type = headers.get("content-type", "application/octet-stream")
        else:
            content_type = getattr(upload, "content_type", "application/octet-stream")

        # Ensure we never return None
        return content_type or "application/octet-stream"

    def is_image(self, content_type):
        """Determine if the content type is an image
        """
        return content_type.startswith("image/")

    def fail(self, message, status=500):
        """Return a failure response
        """
        data = {
            "error": message,
            "status": "error"
        }
        return self.send_json(data, status=status)

    @returns_json
    def send_json(self, data, status=200):
        """Return a JSON response
        """
        self.request.response.setStatus(status)
        return data
