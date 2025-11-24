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

import transaction
from bika.lims import api
from bika.lims import logger
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from senaite.core.events.attachments import AttachmentsDeletedEvent
from senaite.core.interfaces import IMultiUploadFileCreator
from senaite.core.interfaces import IMultiUploadFileRemover
from zope.component import adapter
from zope.event import notify
from zope.interface import Interface
from zope.interface import implementer


@adapter(Interface, Interface)
@implementer(IMultiUploadFileCreator)
class DefaultFileCreator(object):
    """Default adapter for creating File/Image objects from uploaded data

    This adapter creates standard Plone File or Image objects based on the
    content type of the uploaded file. It can be overridden by registering
    a more specific adapter for a particular context or field.
    """

    def __init__(self, context, field):
        """Initialize the adapter

        :param context: The container where files will be created
        :param field: The field being processed
        """
        self.context = context
        self.field = field

    def create(self, filename, content_type, data):
        """Create a File or Image object from uploaded data

        :param filename: The original filename (unicode)
        :param content_type: The MIME content type
        :param data: The binary file data (bytes)
        :returns: The created File or Image object
        """
        # Ensure filename is unicode
        filename = api.safe_unicode(filename)

        # Determine if this is an image based on content type
        is_image = content_type.startswith("image/")

        # Create the appropriate blob type
        if is_image:
            blob = NamedBlobImage(
                data=data,
                filename=filename,
                contentType=content_type
            )
            portal_type = "SimpleImage"
            field_name = "image"
        else:
            blob = NamedBlobFile(
                data=data,
                filename=filename,
                contentType=content_type
            )
            portal_type = "SimpleFile"
            field_name = "file"

        # Create the object in the container
        kwargs = {
            field_name: blob,
            "title": filename,
            "checkConstraints": False,
        }

        try:
            transaction.savepoint()
            api.snapshot.pause_snapshots_for(self.context)
            obj = createContentInContainer(
                self.context,
                portal_type,
                **kwargs
            )
            api.snapshot.resume_snapshots_for(self.context)

            logger.info(u"Created {} object {} with UID {}".format(
                portal_type, filename, api.get_uid(obj)))

            return obj

        except Exception as e:
            import traceback
            logger.error(u"Error creating {} object {}: {}".format(
                portal_type, filename, api.safe_unicode(str(e))))
            logger.error(traceback.format_exc())
            raise


@adapter(Interface)
@implementer(IMultiUploadFileRemover)
class DefaultFileRemover(object):
    """Default adapter for removing File/Image objects

    This adapter removes File/Image objects by deleting them from their
    container. It can be overridden by registering a more specific adapter
    to customize removal behavior, e.g., to move files to a central repository
    instead of deleting them.
    """

    def __init__(self, container):
        """Initialize the adapter

        :param container: The container context
        """
        self.container = container

    def remove(self, uids):
        """Remove SimpleFile/SimpleImage objects by their UIDs

        :param uids: Set or list of UIDs to remove
        """
        if not uids:
            return
        if not isinstance(uids, (list, set, tuple)):
            uids = [uids]

        logger.info("Deleting {} removed file(s) from {}".format(
            len(uids), api.get_path(self.container)))

        # deleted objects for event notification
        deleted = []

        for uid in uids:
            try:
                transaction.savepoint()
                obj = api.get_object(uid)
                # Store info before deletion for logging
                obj_id = api.get_id(obj)
                obj_type = api.get_portal_type(obj)
                obj_path = api.get_path(obj)
                # Delete the object
                api.delete(obj, check_permissions=False)
                logger.info(u"Deleted {} object: {} (was at: {})".format(
                    obj_type, obj_id, obj_path))
                deleted.append(obj)
            except api.APIError as e:
                logger.error("Error deleting object {}: {}".format(
                    repr(obj), str(e)))
                import traceback
                logger.error(traceback.format_exc())
                continue
            except Exception as e:
                logger.error("Unexpected error deleting object {}: {}".format(
                    repr(obj), str(e)))
                import traceback
                logger.error(traceback.format_exc())
                continue

        # Notify about the removed attachments
        notify(AttachmentsDeletedEvent(self.container, deleted))
