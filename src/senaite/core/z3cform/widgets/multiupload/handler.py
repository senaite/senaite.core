# -*- coding: utf-8 -*-

import json
from bika.lims import api
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from Products.Five.browser import BrowserView
from ZODB.blob import Blob


class MultiUploadHandler(BrowserView):
    """Handler for multiupload widget AJAX requests

    This view receives file uploads from the React multiupload widget
    and stores them temporarily, returning a unique ID for each file.
    """

    def __call__(self):
        """Handle the upload request"""
        self.request.response.setHeader('Content-Type', 'application/json')

        try:
            # Get the uploaded file from request
            file_upload = None
            for key in self.request.form.keys():
                value = self.request.form.get(key)
                if hasattr(value, 'filename') and hasattr(value, 'read'):
                    file_upload = value
                    break

            if not file_upload:
                return json.dumps({
                    'error': 'No file uploaded',
                    'status': 'error'
                })

            # Get file metadata
            filename = getattr(file_upload, 'filename', 'unknown')

            # Get content type from headers
            headers = getattr(file_upload, 'headers', {})
            if hasattr(headers, 'get'):
                content_type = headers.get('content-type', 'application/octet-stream')
            else:
                content_type = getattr(file_upload, 'content_type', 'application/octet-stream')

            # Read file data
            file_data = file_upload.read()

            # Determine if it's an image
            is_image = content_type.startswith('image/')

            # Create blob
            if is_image:
                blob = NamedBlobImage(
                    data=file_data,
                    filename=filename,
                    contentType=content_type
                )
            else:
                blob = NamedBlobFile(
                    data=file_data,
                    filename=filename,
                    contentType=content_type
                )

            # Store the blob in the session for later retrieval
            # Generate a unique ID for this upload
            import uuid
            upload_id = str(uuid.uuid4())

            # Store in session
            session = self.request.SESSION
            if 'multiupload_files' not in session:
                session['multiupload_files'] = {}

            session['multiupload_files'][upload_id] = {
                'blob': blob,
                'filename': filename,
                'content_type': content_type,
                'is_image': is_image,
            }

            return json.dumps({
                'id': upload_id,
                'filename': filename,
                'content_type': content_type,
                'size': len(file_data),
                'status': 'success'
            })

        except Exception as e:
            api.logger.error("Error handling file upload: {}".format(str(e)))
            return json.dumps({
                'error': str(e),
                'status': 'error'
            })
