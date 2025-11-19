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
from senaite.core.interfaces import IMultiUploadFileCreator
from senaite.core.interfaces import IMultiUploadFileRemover
from zope.component import getAdapter
from zope.component import getMultiAdapter


class MultiFileUploadWidget(ReferenceWidget):
    """Widget for uploading files that creates File/Image objects
    and stores their UIDs as references.

    This widget integrates with the React multiupload widget to:
    1. Accept file uploads, even in add forms
    2. Create File or Image objects for each uploaded file
    3. Store them in the current context
    4. Store the UIDs of created objects in the field
    """

    # CSS class that is picked up by the ReactJS component
    klass = u"multiuploadfield"

    _properties = ReferenceWidget._properties.copy()
    _properties.update({
        # Use our custom template
        "macro": "senaite_widgets/multifileuploadwidget",
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
        return super(MultiFileUploadWidget, self).get_value(
            context, field, value)

    def get_input_widget_attributes(self, context, field, value):
        """Return input widget attributes for the ReactJS multiupload component

        This method is called from the page template to populate the
        data attributes that are used by the ReactJS widget component.

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

        attributes = {
            "data-fieldname": field.getName(),
            "data-endpoint": endpoint,
            "data-portal_url": portal_url,
            "data-context_url": context_url,
            "data-max_filesize": max_filesize,
            "data-accepted_types": json.dumps(accepted_types),
        }

        return attributes

    def is_multi_valued(self, field):
        """Check if the field accepts multiple values

        :param field: The current field
        :returns: True if multi-valued, False otherwise
        """
        return getattr(field, "multiValued", False)

    def get_download_url(self, obj):
        """Get the download URL for a File or Image object

        :param obj: The File or Image object
        :returns: Download URL string
        """
        url = api.get_url(obj)
        portal_type = api.get_portal_type(obj)

        # For Dexterity File/Image objects, use the @@download view
        if portal_type == "File":
            return "{}/@@download/file".format(url)
        elif portal_type == "Image":
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
            # Image objects use 'image' field, File objects use 'file' field
            field_name = "image" if portal_type == "Image" else "file"

        # get the file object from the field
        file_obj = getattr(obj, field_name, None)

        if file_obj and hasattr(file_obj, "size"):
            return file_obj.size
        elif file_obj and hasattr(file_obj, "getSize"):
            return file_obj.getSize()

        return 0

    def get_existing_files_data(self, context, field, value):
        """Get metadata for existing file references to populate React component

        :param context: The current context of the field
        :param field: The current field of the widget
        :param value: The current field value (list of UIDs or objects)
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
                logger.error("Could not retrieve object for UID: {}".format(uid))
                continue

        return json.dumps(existing_files)

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """Process form data and create File/Image objects from uploads

        This method:
        1. Gets the main field value which contains existing UIDs
        2. Gets uploaded file IDs from the .data field (stored by multiupload handler)
        3. Creates File or Image objects for new uploads
        4. Deletes File/Image objects that were removed
        5. Returns the combined list of existing + new UIDs to be stored
        """
        # Skip processing for temporary instances
        if instance.isTemporary():
            return [], {}

        # Get current field value (before form processing)
        field_name = field.getName()
        old_value = field.get(instance)
        old_uids = []
        if old_value:
            if isinstance(old_value, (list, tuple)):
                old_uids = [api.get_uid(obj) for obj in old_value if api.is_object(obj)]
            elif api.is_object(old_value):
                old_uids = [api.get_uid(old_value)]

        # Get the main field value (existing UIDs maintained by React)
        main_value = form.get(field_name, "")
        existing_uids = []
        if main_value:
            if api.is_string(main_value):
                # UIDs are separated by \r\n
                existing_uids = [uid.strip() for uid in main_value.split("\r\n") if uid.strip()]
            elif isinstance(main_value, (list, tuple)):
                existing_uids = [uid for uid in main_value if uid]

        logger.info("process_form for field '{}': old_uids = {}, existing_uids from main field = {}".format(
            field_name, old_uids, existing_uids))

        # Get the JSON data from the .data hidden field (new uploads only)
        # It contains the generated UUIDs for uploaded files
        data_field = field_name + ".data"
        data = form.get(data_field, "")

        # Start with existing UIDs
        uids = list(existing_uids)

        # Parse upload IDs if there are new uploads
        upload_ids = []
        if data:
            try:
                # Parse the JSON data containing upload IDs for new files
                # E.g. [u'27fceb0e-a750-430f-b1ab-b93e0c902fb3', ...]
                upload_ids = json.loads(data)
                logger.info("process_form for field '{}': upload_ids from .data "
                            "field = {}".format(field_name, upload_ids))
            except (ValueError, TypeError):
                logger.error("Invalid JSON data for field {}".format(field_name))
                upload_ids = []

        # Get uploaded files from session
        session = instance.REQUEST.SESSION
        uploaded_files = session.get("multiupload_files", {})

        # Track created UIDs in session to handle multiple process_form calls
        # (which happens during validation)
        created_uids_key = "multiupload_created_uids"
        created_uids_map = session.get(created_uids_key, {})

        # Create File/Image objects for each uploaded file
        for upload_id in upload_ids:
            # Check if we already created an object for this upload_id
            if upload_id in created_uids_map:
                # Reuse the UID from a previous process_form call
                uid = created_uids_map[upload_id]
                uids.append(uid)
                logger.info("Reusing existing UID {} for upload_id {}".format(
                    uid, upload_id))
                continue

            if upload_id in uploaded_files:
                file_data = uploaded_files[upload_id]

                data = file_data["data"]
                filename = api.safe_unicode(file_data["filename"])
                content_type = file_data["content_type"]

                try:
                    # Get the file creator adapter
                    creator = getMultiAdapter(
                        (instance, field), IMultiUploadFileCreator)

                    # Create the File/Image object using the adapter
                    obj = creator.create(filename, content_type, data)

                    # Get UID
                    uid = api.get_uid(obj)
                    uids.append(uid)

                    # Store the UID for this upload_id in session
                    created_uids_map[upload_id] = uid
                    session[created_uids_key] = created_uids_map

                except Exception as e:
                    import traceback
                    logger.error(u"Error creating object {}: {}".format(
                        filename, api.safe_unicode(str(e))))
                    logger.error(traceback.format_exc())
                    continue
            else:
                logger.warning("Upload ID {} not found in session, skipping"
                               .format(upload_id))

        logger.info("process_form for field '{}': final UIDs to be stored = {}"
                    .format(field_name, uids))

        # Delete File/Image objects that were removed from the field
        logger.info("Checking deletion: validating={}, old_uids={}, uids={}".format(
            validating, old_uids, uids))

        if old_uids:
            removed_uids = set(old_uids) - set(uids)
            logger.info("Removed UIDs: {}".format(removed_uids))
            if removed_uids:
                self.delete_removed_files(instance, removed_uids)

        # Handle multi-valued vs single-valued
        if not self.is_multi_valued(field):
            return uids[0] if uids else "", {}

        return uids, {}

    def delete_removed_files(self, container, uids):
        """Delete File/Image objects that were removed from the field

        :param container: The parent container
        :param uids: List of UIDs to delete
        """
        if not uids:
            return

        # Remove the files using the `IMultiUploadFileRemover` adapter
        remover = getAdapter(container, IMultiUploadFileRemover)
        remover.remove(uids)


registerWidget(MultiFileUploadWidget,
               title="Multi File Upload Widget",
               description="Widget for uploading files into the parent container keeping UID references",
               used_for=("bika.lims.browser.fields.UIDReferenceField",))
