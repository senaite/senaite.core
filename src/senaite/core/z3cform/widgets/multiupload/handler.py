# -*- coding: utf-8 -*-

import threading
import uuid

from bika.lims import api
from bika.lims.decorators import returns_json
from Products.Five.browser import BrowserView
from senaite.core import logger

# Global lock for session access - shared across all threads
SESSION_LOCK = threading.Lock()
SESSION_KEY = "multiupload_files"


class MultiUploadHandler(BrowserView):
    """Handler for multiupload widget AJAX requests

    This view receives file uploads from the React multiupload widget
    and stores them temporarily in the session, returning a unique ID.
    The actual File/Image objects are created later in the widget's
    process_form method.
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
        """Store the uploaded file temporarily in the session

        NOTE: Uses a global threading.Lock to prevent race conditions
              when multiple threads try to write to the session
              simultaneously.

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

        # Store in session with thread-safe locking
        success = self.store_in_session(
            upload_id, filename, content_type, data)

        if not success:
            return self.fail("Failed to store file in session", 500)

        return self.send_json({
            "id": upload_id,
            "filename": filename,
            "content_type": content_type,
            "size": file_size,
            "status": "success"
        })

    def store_in_session(
            self, upload_id, filename, content_type, data):
        """Store uploaded file data in session with thread-safe locking

        :param upload_id: The unique upload ID
        :param filename: The filename
        :param content_type: The MIME type
        :param data: The file data bytes
        :returns: True if stored successfully, False otherwise
        """
        with SESSION_LOCK:
            logger.info(
                u"Acquired lock for upload {}".format(upload_id))

            # IMPORTANT: Sync the ZODB connection to get fresh data
            # Without this, we see stale data from transaction snapshot
            session = self.request.SESSION
            # Sync ZODB connection if available
            if hasattr(session, '_p_jar') and \
                    session._p_jar is not None:
                session._p_jar.sync()

            # Get or create the uploads dict
            uploaded_files = session.get(SESSION_KEY, {})

            # Add this upload
            uploaded_files[upload_id] = {
                "data": data,
                "filename": filename,
                "content_type": content_type,
            }

            # Store back to session - triggers ZODB change detection
            session[SESSION_KEY] = uploaded_files

            # Verify it was stored
            total = len(session.get(SESSION_KEY, {}))
            if upload_id in session.get(SESSION_KEY, {}):
                logger.info(
                    u"✓ Stored upload {} for file {} (total: {})"
                    .format(upload_id, filename, total))
                logger.info(
                    u"Released lock for upload {}".format(upload_id))
                return True
            else:
                logger.error(
                    u"✗ FAILED to store upload {} for file {}"
                    .format(upload_id, filename))
                logger.info(
                    u"Released lock for upload {}".format(upload_id))
                return False

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
