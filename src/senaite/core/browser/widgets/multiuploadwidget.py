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

import json

from bika.lims import api
from bika.lims import logger
from Products.Archetypes.Registry import registerWidget
from senaite.core.browser.widgets.referencewidget import ReferenceWidget


class MultiUploadWidget(ReferenceWidget):
    """Widget for uploading files that creates File/Image objects
    and stores their UIDs as references.

    This widget integrates with the React multiupload widget to:
    1. Accept file uploads, even in add forms
    2. Create File or Image objects for each uploaded file
    3. Store them as child objects of the current context
    4. Store the UIDs of the created objects in the reference field
    """

    # CSS class that is picked up by the ReactJS component
    klass = u"multiuploadfield"

    _properties = ReferenceWidget._properties.copy()
    _properties.update({
        # Use our custom template
        "macro": "senaite_widgets/multiuploadwidget",
        "endpoint": "@@multiupload_handler",
        # Maximum file size (10MB default)
        "max_filesize": 10485760,
        # Accept all file types by default
        "accepted_types": {},
    })

    def get_value(self, context, field, value=None):
        """Extract the value from the request or get it from the field

        :param context: The current context of the field
        :param field: The current field of the widget
        :param value: The current set value
        :returns: List of UIDs
        """
        return super(MultiUploadWidget, self).get_value(
            context, field, value)

    def get_input_widget_attributes(self, context, field, value):
        """Return input widget attributes for the ReactJS widget

        This method is called from the page template to populate the
        data attributes used by the ReactJS widget component.

        :param context: The current context of the field
        :param field: The current field of the widget
        :param value: The current field value (list of UIDs)
        :returns: Dictionary of HTML data attributes
        """
        portal = api.get_portal()
        portal_url = api.get_url(portal)
        context_url = api.get_url(context)
        endpoint = getattr(self, "endpoint", "@@multiupload_handler")
        max_filesize = getattr(self, "max_filesize", 10485760)
        accepted_types = getattr(self, "accepted_types", {})

        # Generate widget ID
        widget_id = "{}_{}".format(context.getId(), field.getName())

        attributes = {
            "id": widget_id,
            "data-fieldname": field.getName(),
            "data-endpoint": endpoint,
            "data-portal_url": portal_url,
            "data-context_url": context_url,
            "data-max_filesize": max_filesize,
            "data-accepted_types": json.dumps(accepted_types),
        }

        return attributes

    def get_download_url(self, obj):
        """Get the download URL for a File or Image object

        :param obj: The File or Image object
        :returns: Download URL string
        """
        url = api.get_url(obj)
        portal_type = api.get_portal_type(obj)

        # Use @@download view
        if portal_type == "SimpleFile":
            return "{}/@@download/file".format(url)
        elif portal_type == "SimpleImage":
            return "{}/@@download/image".format(url)

        # Fallback to object URL
        return url

    def get_file_size(self, obj, field_name=None):
        """Get the file size for a File or Image object

        :param obj: The File or Image object
        :returns: File size in bytes, or 0 if not available
        """
        if field_name is None:
            portal_type = api.get_portal_type(obj)
            # Image uses 'image' field, File uses 'file' field
            field_name = "image" if portal_type == "Image" else "file"

        # get the file object from the field
        file_obj = getattr(obj, field_name, None)

        if file_obj and hasattr(file_obj, "size"):
            return file_obj.size
        elif file_obj and hasattr(file_obj, "getSize"):
            return file_obj.getSize()

        return 0

    def get_existing_files_data(self, context, field, value):
        """Get metadata for existing file references

        :param context: The current context of the field
        :param field: The current field of the widget
        :param value: The current field value (list of UIDs)
        :returns: JSON string with existing file data
        """
        existing_files = []
        uids = self.get_value(context, field, value)

        for uid in uids:
            try:
                obj = api.get_object(uid)
                file_data = {
                    "uid": uid,
                    "name": api.get_title(obj),
                    "url": self.get_download_url(obj),
                    "type": api.get_portal_type(obj),
                    "size": self.get_file_size(obj),
                }
                existing_files.append(file_data)

            except api.APIError:
                logger.error(
                    "Could not retrieve object for UID: {}"
                    .format(uid))
                continue

        return json.dumps(existing_files)

    def process_form(self, instance, field, form,
                     empty_marker=None, emptyReturnsMarker=False,
                     validating=True):
        """Process form data and return existing UIDs

        :param instance: The content instance
        :param field: The field being processed
        :param form: The form data
        :param empty_marker: Empty marker value
        :param emptyReturnsMarker: Whether to return empty marker
        :param validating: Whether we are validating
        :returns: Tuple of (existing_uids, kwargs)
        """
        # Skip processing for temporary instances
        if instance.isTemporary():
            return [], {}

        field_name = field.getName()
        logger.info("=" * 80)
        logger.info(
            "process_form() called for field '{}', validating={}"
            .format(field_name, validating))

        # Always return the existing UIDs from the field.
        # The file creation/deletion and adding is handled in the event handler
        existing_uids = field.getRaw(instance) or []

        logger.info(
            "process_form for field '{}': returning existing UIDs = {}"
            .format(field_name, existing_uids))

        # Return only existing UIDs
        return existing_uids, {}


registerWidget(
    MultiUploadWidget,
    title="Multi Upload Widget",
    description=(
        "Widget for uploading files into the parent container "
        "keeping UID references"),
    used_for=("bika.lims.browser.fields.UIDReferenceField",))
