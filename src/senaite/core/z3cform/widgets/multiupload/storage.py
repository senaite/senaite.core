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

import time

from bika.lims import api
from BTrees.OOBTree import OOBTree
from persistent import Persistent
from senaite.core import logger
from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface
from zope.interface import implementer

__doc__ = """
Temporary upload storage for multiupload widget

This module provides a cluster-safe storage mechanism for temporarily
storing uploaded files before they are converted to actual File/Image
objects. Unlike SESSION storage, this storage is properly shared across
all ZEO clients via ZODB.
"""

# Storage key in portal annotations
STORAGE_KEY = "senaite.core.multiupload.storage"

# Default expiration time for uploads (2 hours)
DEFAULT_EXPIRATION_SECONDS = 7200


class ITemporaryUploadStorage(Interface):
    """Interface for temporary upload storage"""

    def store(upload_id, filename, content_type, data):
        """Store uploaded file data

        :param upload_id: Unique identifier for the upload
        :param filename: Name of the uploaded file
        :param content_type: MIME type of the file
        :param data: Binary file data
        :returns: True if stored successfully
        """

    def retrieve(upload_id):
        """Retrieve uploaded file data

        :param upload_id: Unique identifier for the upload
        :returns: Dictionary with file data or None if not found
        """

    def remove(upload_id):
        """Remove uploaded file data

        :param upload_id: Unique identifier for the upload
        :returns: True if removed successfully
        """

    def cleanup(max_age_seconds=DEFAULT_EXPIRATION_SECONDS):
        """Remove uploads older than specified age

        :param max_age_seconds: Maximum age in seconds
        :returns: Number of uploads removed
        """


@implementer(ITemporaryUploadStorage)
class TemporaryUploadStorage(object):
    """Cluster-safe temporary storage for uploaded files

    This implementation uses portal annotations to store uploads in a
    shared ZODB container that is accessible to all ZEO clients.

    Each upload is stored with a unique UUID key, preventing conflicts
    between concurrent uploads from different users.
    """

    def __init__(self, context=None):
        """Initialize the storage

        :param context: Context object (usually portal)
        """
        self.context = context or api.get_portal()

    def _get_container(self):
        """Get or create the storage container

        Uses OOBTree which has built-in ZODB conflict resolution for
        concurrent writes of different keys.

        :returns: OOBTree container for uploads
        """
        annotations = IAnnotations(self.context)
        if STORAGE_KEY not in annotations:
            container = OOBTree()
            annotations[STORAGE_KEY] = container
        return annotations[STORAGE_KEY]

    def store(self, upload_id, filename, content_type, data):
        """Store uploaded file data

        Thread-safe and cluster-safe. Multiple concurrent uploads with
        different upload_ids will not conflict.

        Also triggers automatic cleanup of expired uploads periodically.

        :param upload_id: Unique identifier for the upload
        :param filename: Name of the uploaded file
        :param content_type: MIME type of the file
        :param data: Binary file data
        :returns: True if stored successfully
        """
        try:
            self.cleanup()

            container = self._get_container()

            # Create upload record
            upload_record = UploadRecord(
                upload_id=upload_id,
                filename=filename,
                content_type=content_type,
                data=data
            )

            # Store in container - OOBTree handles concurrent additions
            container[upload_id] = upload_record

            logger.info(
                u"Stored upload {} for file {} ({} bytes)".format(
                    upload_id, filename, len(data)))

            return True

        except Exception as e:
            logger.error(
                u"Failed to store upload {}: {}".format(
                    upload_id, api.safe_unicode(str(e))))
            return False

    def retrieve(self, upload_id):
        """Retrieve uploaded file data

        :param upload_id: Unique identifier for the upload
        :returns: Dictionary with file data or None if not found
        """
        try:
            container = self._get_container()
            record = container.get(upload_id)

            if record is None:
                logger.warning(
                    u"Upload {} not found in storage".format(upload_id))
                return None

            # Return as dictionary
            return {
                "filename": record.filename,
                "content_type": record.content_type,
                "data": record.data,
                "timestamp": record.timestamp
            }

        except Exception as e:
            logger.error(
                u"Failed to retrieve upload {}: {}".format(
                    upload_id, api.safe_unicode(str(e))))
            return None

    def remove(self, upload_id):
        """Remove uploaded file data

        :param upload_id: Unique identifier for the upload
        :returns: True if removed successfully
        """
        try:
            container = self._get_container()
            if upload_id in container:
                del container[upload_id]
                logger.info(u"Removed upload {}".format(upload_id))
                return True
            return False

        except Exception as e:
            logger.error(
                u"Failed to remove upload {}: {}".format(
                    upload_id, api.safe_unicode(str(e))))
            return False

    def cleanup(self, max_age_seconds=DEFAULT_EXPIRATION_SECONDS):
        """Remove uploads older than specified age

        This should be called periodically (e.g., via cron job) to
        prevent the storage from growing indefinitely.

        :param max_age_seconds: Maximum age in seconds
        :returns: Number of uploads removed
        """
        try:
            container = self._get_container()
            cutoff_time = time.time() - max_age_seconds
            to_remove = []

            # Find expired uploads
            for upload_id, record in container.items():
                if getattr(record, "timestamp", 0) < cutoff_time:
                    to_remove.append(upload_id)

            # Remove expired uploads
            for upload_id in to_remove:
                del container[upload_id]

            if to_remove:
                logger.info(
                    u"Cleaned up {} expired upload(s)".format(
                        len(to_remove)))

            return len(to_remove)

        except Exception as e:
            logger.error(
                u"Failed to cleanup uploads: {}".format(
                    api.safe_unicode(str(e))))
            return 0


class UploadRecord(Persistent):
    """Persistent record for a single upload

    Stores file data and metadata in ZODB.
    """

    def __init__(self, upload_id, filename, content_type, data):
        """Initialize upload record

        :param upload_id: Unique identifier
        :param filename: File name
        :param content_type: MIME type
        :param data: Binary file data
        """
        self.upload_id = upload_id
        self.filename = filename
        self.content_type = content_type
        self.data = data
        self.timestamp = time.time()


def get_storage(context=None):
    """Get the temporary upload storage utility

    Convenience function to get storage instance.

    :param context: Optional context object
    :returns: ITemporaryUploadStorage implementation
    """
    return TemporaryUploadStorage(context)
