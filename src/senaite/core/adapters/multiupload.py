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

from bika.lims import api
from bika.lims import logger
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from senaite.core.interfaces import IMultiUploadFileCreator
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


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
            portal_type = "Image"
            field_name = "image"
        else:
            blob = NamedBlobFile(
                data=data,
                filename=filename,
                contentType=content_type
            )
            portal_type = "File"
            field_name = "file"

        # Create the object in the container
        kwargs = {
            field_name: blob,
            "title": filename,
            "checkConstraints": False,
        }

        try:
            obj = createContentInContainer(
                self.context,
                portal_type,
                **kwargs
            )

            # Reindex to update catalogs
            obj.reindexObject()

            logger.info(u"Created {} object {} with UID {}".format(
                portal_type, filename, api.get_uid(obj)))

            return obj

        except Exception as e:
            import traceback
            logger.error(u"Error creating {} object {}: {}".format(
                portal_type, filename, api.safe_unicode(str(e))))
            logger.error(traceback.format_exc())
            raise
