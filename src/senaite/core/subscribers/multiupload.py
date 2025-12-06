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
from senaite.core.interfaces import IMultiUploadFileCreator
from senaite.core.interfaces import IMultiUploadFileRemover
from senaite.core.schema.interfaces import IMultiUploadField
from senaite.core.z3cform.widgets.multiupload.storage import get_storage
from zope.component import getAdapter
from zope.component import getMultiAdapter

# Request attribute key for storing objects being processed
UPLOAD_PROCESSING_KEY = "_multiupload_processing"
UPLOAD_DELETING_KEY = "_multiupload_deleting"

_marker = object()


def on_object_added(obj, event):
    """Event handler for when object is added to container

    (DX: IObjectAddedEvent, AT: IObjectInitializedEvent)

    We use IObjectAddedEvent instead of IObjectCreatedEvent because
    IObjectCreatedEvent fires before the object is added to its container.
    At that stage, the object has no UID, no acquisition chain, and cannot
    be used as a container to create File/Image child objects.

    IObjectAddedEvent fires after the object is fully added to the
    container and has a proper acquisition chain, allowing us to create
    child objects inside it.
    """
    process_multiupload_fields(obj, event)


def on_object_modified(obj, event):
    """Event handler for object modification

    (DX: IObjectModifiedEvent, AT: IObjectEditedEvent)

    Processes MultiUploadField fields after the object is modified.
    Also handles deletion of removed File/Image objects.
    """

    # Early check: does object have MultiUploadField fields?
    fields = get_multiupload_fields(obj)
    if not fields:
        return  # No multiupload fields, skip entirely

    # Get request
    request = api.get_request()
    if not request:
        # Use test request if no real request is available (e.g., test setup)
        request = api.get_test_request()

    # Check for upload data OR submitted UIDs (for deletion detection)
    if not has_multiupload_activity(fields, request, obj):
        return  # No multiupload activity

    # Prevent infinite recursion for deletion handler
    processing_objs = getattr(request, UPLOAD_DELETING_KEY, set())

    obj_uid = api.get_uid(obj)
    if obj_uid in processing_objs:
        return

    logger.info("="*80)
    logger.info("on_object_modified called for {}".format(api.get_path(obj)))

    # Mark this object as being processed for deletions
    processing_objs.add(obj_uid)
    setattr(request, UPLOAD_DELETING_KEY, processing_objs)

    try:
        # Track current values before processing (for deletion detection)
        current_values = track_current_uids(fields, obj)

        # Process uploads (create new File/Image objects from UUIDs)
        process_multiupload_fields(obj, event)

        # Remove files that were deleted from fields
        remove_deleted_files(fields, obj, current_values, request)

    finally:
        # Always remove from processing set
        processing_objs.discard(obj_uid)
        setattr(request, UPLOAD_DELETING_KEY, processing_objs)


def process_multiupload_fields(obj, event):
    """Create File/Image objects from upload UUIDs

    This handler processes all MultiUploadField fields on the object and
    creates File/Image objects for any upload UUIDs that were submitted
    in the form request.

    Called for:
    - IObjectAddedEvent (DX) - after object added to container
    - IObjectModifiedEvent (DX) - after object modified
    """
    # Prevent infinite recursion: check if we're already processing this object
    request = api.get_request()
    if not request:
        # Use test request if no real request is available (e.g., test setup)
        request = api.get_test_request()

    processing_objs = getattr(request, UPLOAD_PROCESSING_KEY, set())

    obj_uid = api.get_uid(obj)
    if obj_uid in processing_objs:
        # Already processing this object, skip to prevent recursion
        return

    # Get all MultiUploadField fields - early return if none
    fields = get_multiupload_fields(obj)
    if not fields:
        return  # No fields to process

    # Check for upload data - early return if none
    if not has_upload_uuids(fields, request, obj):
        return  # No upload data

    # Determine form prefix (needed later for processing)
    form_prefix = "form.widgets." if api.is_dexterity_content(obj) else ""

    # NOW log (only if we're actually processing)
    logger.info("="*80)
    logger.info("process_multiupload_fields called for {}".format(
        api.get_path(obj)))

    # Mark this object as being processed
    processing_objs.add(obj_uid)
    setattr(request, UPLOAD_PROCESSING_KEY, processing_objs)

    try:
        # Get the shared upload storage (cluster-safe)
        storage = get_storage()

        # Process each MultiUploadField
        for name, field in fields.items():
            logger.info("Processing MultiUploadField: {}".format(name))

            # Get submitted UIDs from request (what user wants to keep)
            submitted_uids = get_submitted_uids(
                name, request, prefix=form_prefix, default=[])

            logger.info("Field {} submitted UIDs: {}".format(
                name, submitted_uids))

            # Parse upload UUIDs from request (new files to create)
            upload_uuids = get_upload_uuids(name, request, prefix=form_prefix)

            logger.info("Field {} upload UUIDs: {}".format(
                name, upload_uuids))

            # Create File/Image objects for each upload UUID
            created_uids = []
            for upload_uuid in upload_uuids:
                # Retrieve file data from shared storage
                file_data = storage.retrieve(upload_uuid)
                if not file_data:
                    logger.warning(
                        "Upload data for UUID {} not found in storage"
                        .format(upload_uuid))
                    continue

                # Create file object using adapter
                uid = create_file_object(obj, field, upload_uuid, file_data)
                if uid:
                    created_uids.append(uid)
                    # Mark created object as processing
                    processing_objs.add(uid)
                    # Remove from storage after successful creation
                    storage.remove(upload_uuid)

            # Combine submitted UIDs (existing) with newly created UIDs
            new_value = submitted_uids + created_uids
            logger.info("Updating field {} with value: {}".format(
                name, new_value))
            field.set(obj, new_value)

    finally:
        # Always remove from processing set, even if an error occurred
        processing_objs.discard(obj_uid)
        setattr(request, UPLOAD_PROCESSING_KEY, processing_objs)


def get_upload_uuids(field_name, request, prefix=""):
    """Parse upload UUIDs from request data

    :param field_name: Name of the field
    :param request: The request object
    :param prefix: Form field prefix
    """
    # Get upload UUIDs from request using <fieldname>.data key
    data_key = "{}{}.data".format(prefix, field_name)
    data_value = request.get(data_key, "")

    if not data_value:
        return []

    try:
        upload_data = json.loads(data_value)
        if isinstance(upload_data, list):
            # Filter out empty values and ensure strings
            uuids = [api.safe_unicode(uuid) for uuid in upload_data if uuid]
            logger.info("Parsed {} UUIDs for field {}".format(
                len(uuids), field_name))
            return uuids
    except (ValueError, TypeError) as e:
        logger.error("Error parsing upload data for field {}: {}".format(
            field_name, str(e)))

    return []


def get_submitted_uids(field_name, request, prefix="", default=_marker):
    """Get submitted UIDs from request (what user wants to keep)

    :param field_name: Name of the field
    :param request: The request object
    :param prefix: Form field prefix
    :returns: List of submitted UIDs
    """
    # Get main field value from request (contains existing UIDs)
    field_key = "{}{}".format(prefix, field_name)
    field_value = request.get(field_key, "")

    if not field_value:
        return default

    # Split by newlines and filter UIDs
    submitted = []
    for item in field_value.split("\r\n"):
        item = item.strip()
        if item and api.is_uid(item):
            submitted.append(item)

    return submitted


def create_file_object(obj, field, upload_uuid, file_data):
    """Create a File or Image object from upload data

    :param obj: The container object
    :param field: The field being processed
    :param upload_uuid: UUID of the upload
    :param file_data: Dictionary with file data (data, filename, content_type)
    :returns: UID of created object or None on error
    """
    try:
        data = file_data["data"]
        filename = api.safe_unicode(file_data["filename"])
        content_type = file_data["content_type"]

        # Get the file creator adapter
        creator = getMultiAdapter(
            (obj, field),
            IMultiUploadFileCreator
        )

        # Create the File/Image object using the adapter
        file_obj = creator.create(filename, content_type, data)
        uid = api.get_uid(file_obj)

        logger.info("Created object with UID {} for UUID {}".format(
            uid, upload_uuid))
        return uid

    except Exception as e:
        import traceback
        filename = file_data.get("filename", "unknown")
        logger.error(u"Error creating object {}: {}".format(
            filename, api.safe_unicode(str(e))))
        logger.error(traceback.format_exc())
        return None


def get_multiupload_fields(obj):
    """Get all MultiUploadField fields from object

    :param obj: The object to get fields from
    :returns: Dictionary of field name -> field pairs
    """
    fields = api.get_fields(obj)
    return {name: field for name, field in fields.items()
            if IMultiUploadField.providedBy(field)}


def has_multiupload_activity(fields, request, obj):
    """Check if there is any multiupload activity in the request

    Checks for:
    - New upload UUIDs in request (field.data parameter)
    - Field submissions for deletion detection (field parameter)

    :param fields: Dictionary of field name -> field pairs
    :param request: The request object
    :param obj: The object being processed
    :returns: True if there's multiupload activity, False otherwise
    """
    if not fields:
        return False

    # Determine form prefix based on content type
    form_prefix = "form.widgets." if api.is_dexterity_content(obj) else ""

    for name in fields.keys():
        # Check for new uploads
        data_key = "{}{}.data".format(form_prefix, name)
        if request.get(data_key):
            return True

        # Check for field submission (deletion scenario)
        field_key = "{}{}".format(form_prefix, name)
        if field_key in request.form:
            return True

    return False


def has_upload_uuids(fields, request, obj):
    """Check if there are upload UUIDs in the request

    Only checks for new upload UUIDs (field.data parameter),
    not field submissions.

    :param fields: Dictionary of field name -> field pairs
    :param request: The request object
    :param obj: The object being processed
    :returns: True if there are upload UUIDs, False otherwise
    """
    if not fields:
        return False

    # Determine form prefix based on content type
    form_prefix = "form.widgets." if api.is_dexterity_content(obj) else ""

    for name in fields.keys():
        data_key = "{}{}.data".format(form_prefix, name)
        if request.get(data_key):
            return True

    return False


def track_current_uids(fields, obj):
    """Track current UIDs before processing

    :param fields: Dictionary of field name -> field pairs
    :param obj: The object containing the fields
    :returns: Dictionary of field name -> list of current UIDs
    """
    current_values = {}
    for name, field in fields.items():
        current_uids = get_current_uids(field, obj)
        current_values[name] = current_uids
        logger.info("Field {} current UIDs: {}".format(name, current_uids))
    return current_values


def get_current_uids(field, obj):
    """Get current UIDs stored in field

    :param field: The field to read
    :param obj: The object containing the field
    :returns: List of current UIDs in field
    """
    current_value = field.get(obj) or []
    return list(map(api.get_uid, current_value))


def remove_deleted_files(fields, obj, current_values, request):
    """Remove files that were deleted from fields

    Compares current UIDs (what's in the field now) with submitted UIDs
    (what the user wants to keep) to determine which files to delete.

    :param fields: Dictionary of field name -> field pairs
    :param obj: The object containing the fields
    :param current_values: Dictionary of current UIDs per field
    :param request: The request object
    """
    form_prefix = ""
    if api.is_dexterity_content(obj):
        form_prefix = "form.widgets."

    for name, field in fields.items():
        # Get submitted UIDs (what user wants to keep)
        submitted_uids = get_submitted_uids(name, request, prefix=form_prefix)
        if submitted_uids is _marker:
            # field is missing in request, which means we are not coming from a
            # form submission, but rather from a programmatic modification
            continue
        logger.info("Field {} submitted UIDs: {}".format(
            name, submitted_uids))

        # Get new field value after processing (includes newly created)
        new_uids = get_current_uids(field, obj)
        logger.info("Field {} new UIDs: {}".format(name, new_uids))

        # Find removed UIDs: what was there before but not submitted
        current_uids = current_values.get(name, [])
        removed_uids = set(current_uids) - set(submitted_uids)

        if removed_uids:
            logger.info("Field {}: Deleting {} removed file(s): {}".format(
                name, len(removed_uids), removed_uids))

            # Use the remover adapter to delete the files
            remover = getAdapter(obj, IMultiUploadFileRemover)
            remover.remove(removed_uids)
