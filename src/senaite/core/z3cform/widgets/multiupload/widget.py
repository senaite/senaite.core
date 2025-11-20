# -*- coding: utf-8 -*-

import json

from bika.lims import api
from bika.lims import logger
from senaite.core.interfaces import IMultiUploadFileCreator
from senaite.core.interfaces import IMultiUploadFileRemover
from senaite.core.interfaces import IMultiUploadWidget
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import IUIDReferenceField
from senaite.core.z3cform.widgets.uidreference.widget import UIDReferenceWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import implementer_only


@implementer_only(IMultiUploadWidget)
class MultiUploadWidget(UIDReferenceWidget):
    """Multi-file upload widget using React and react-dropzone
    """

    klass = u"multiuploadfield"
    value = ()

    def update(self):
        super(MultiUploadWidget, self).update()

    @property
    def portal_url(self):
        """Return the portal URL"""
        return api.get_url(api.get_portal())

    @property
    def context_url(self):
        """Return the context URL"""
        return api.get_url(self.context)

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
        :param field_name: Optional field name to check for size. If None,
                          automatically determines based on portal type.
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

    def get_existing_files_data(self):
        """Get metadata for existing file references to populate React component

        :returns: List of existing file data dicts
        """
        existing_files = []
        value = self.value or ()

        for uid in value:
            if not uid:
                continue
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
                    "Could not retrieve object for UID: {}".format(uid))
                continue

        return existing_files

    def get_session(self, request):
        """Safely get the session from the request

        :param request: The request object
        :returns: Session object or None if not available (e.g., in tests)
        """
        return getattr(request, "SESSION", None)

    def get_value(self):
        """Extract the value from the widget

        Returns the current UIDs as a list
        """
        value = self.value
        if value is None:
            return []
        if not isinstance(value, (list, tuple)):
            return []
        return list(value)

    def get_input_widget_attributes(self):
        """Return input widget attributes for the ReactJS component

        This method gets called from the page template to populate the
        attributes that are used by the ReactJS widget component.
        """
        existing_files = self.get_existing_files_data()

        attributes = {
            "id": self.id,
            "data-fieldname": self.name,
            "data-portal_url": self.portal_url,
            "data-context_url": self.context_url,
            "data-endpoint": "@@multiupload_handler",
            "data-max_filesize": json.dumps(10485760),  # 10MB
            "data-accepted_types": json.dumps({}),  # Accept all
            "data-existing_files": json.dumps(existing_files),
        }

        return attributes

    def extract(self, default=None):
        """Extract uploaded files from request and create File/Image objects

        Returns the final list of UIDs (existing + newly created)
        """
        logger.info("="*80)
        logger.info("extract() called for field '{}'".format(self.name))

        # Get existing Plone UIDs from the main field (maintained by React)
        main_value = self.request.form.get(self.name, "")
        existing_uids = []
        if main_value:
            # Split by newlines
            existing_uids = [uid.strip() for uid in main_value.split("\r\n")]

        logger.info("extract for field '{}': existing_uids={}".format(
            self.name, existing_uids))

        # Start with existing UIDs
        uids = list(existing_uids)

        # Get upload IDs from the .data field (new uploads)
        data_field = self.name + '.data'
        data = self.request.form.get(data_field, None)
        upload_ids = []

        if data:
            try:
                # Parse the JSON data containing upload IDs
                upload_ids = json.loads(data)
                if not isinstance(upload_ids, (list, tuple)):
                    upload_ids = []
            except (ValueError, TypeError):
                logger.error(
                    "Invalid JSON data for field {}".format(self.name))
                upload_ids = []

        logger.info("extract for field '{}': upload_ids={}".format(
            self.name, upload_ids))

        # Get session and uploaded files
        session = self.get_session(self.request)
        if not session:
            # No session (e.g., in tests), return existing UIDs only
            logger.info(
                "No SESSION available, skipping file upload processing")
            return uids

        uploaded_files = session.get("multiupload_files", {})

        # Track created UIDs to handle multiple extract calls
        created_uids_key = "multiupload_created_uids"
        created_uids_map = session.get(created_uids_key, {})

        # Create File/Image objects for each uploaded file
        for upload_id in upload_ids:
            # Check if we already created an object for this upload_id
            if upload_id in created_uids_map:
                uid = created_uids_map[upload_id]
                # Verify the object still exists (might have been rolled back)
                try:
                    obj = api.get_object(uid)
                    uids.append(uid)
                    logger.info(
                        "Reusing existing UID {} for upload_id {}".format(
                            uid, upload_id))
                    continue
                except api.APIError:
                    logger.warning(
                        "UID {} from session no longer exists, "
                        "recreating for upload_id {}".format(
                            uid, upload_id))
                    # Remove stale UID from map and fall through to recreate
                    del created_uids_map[upload_id]
                    session[created_uids_key] = created_uids_map

            # Get file data from session dict
            file_data = uploaded_files.get(upload_id)

            logger.info(
                "Looking for upload_id {} in session dict".format(
                    upload_id))

            if file_data:
                data = file_data["data"]
                filename = api.safe_unicode(file_data["filename"])
                content_type = file_data["content_type"]

                try:
                    # Get the file creator adapter
                    creator = getMultiAdapter(
                        (self.context, self.field),
                        IMultiUploadFileCreator
                    )

                    # Create the File/Image object using the adapter
                    obj = creator.create(filename, content_type, data)

                    # Get UID
                    uid = api.get_uid(obj)
                    uids.append(uid)

                    # Store the UID for this upload_id in session
                    created_uids_map[upload_id] = uid
                    session[created_uids_key] = created_uids_map

                    logger.info(
                        "Created object with UID {} for upload_id {}"
                        .format(uid, upload_id))
                    logger.info(
                        "Created and mapped: upload_id {} -> UID {}"
                        .format(upload_id, uid))

                except Exception as e:
                    import traceback
                    logger.error(u"Error creating object {}: {}".format(
                        filename, api.safe_unicode(str(e))))
                    logger.error(traceback.format_exc())
                    continue
            else:
                logger.warning(
                    "Upload file data for ID {} not found in session, "
                    "skipping".format(upload_id))

        logger.info("extract for field '{}': final UIDs={}".format(
            self.name, uids))

        # Always return the list of UIDs, even if empty
        # Returning None/default could cause the field to not be set
        return uids


@adapter(IUIDReferenceField, IMultiUploadWidget)
@implementer(IDataConverter)
class MultiUploadDataConverter(BaseDataConverter):
    """Data converter for multi-upload widget
    """

    def toWidgetValue(self, value):
        """Convert from field value (UIDs) to widget value

        :param value: List of UIDs
        :returns: List of UIDs
        """
        if value is None:
            return []
        return value

    def toFieldValue(self, value):
        """Convert from widget value to field value

        The extract() method already created the File/Image objects and
        returned their UIDs.

        :param value: List of Plone UIDs from extract()
        :returns: List/Tuple of UIDs (properly validated)
        """
        # Get the field and context
        field = self.field
        context = self.widget.context

        # Get current field value (old UIDs before form processing)
        old_value = field.get(context)
        old_uids = list(map(api.get_uid, old_value)) if old_value else []

        # Value from extract() is already a list of UIDs
        if value is None:
            uids = []
        else:
            uids = list(value)

        logger.info(
            "toFieldValue for field '{}': old_uids={}, new_uids={}"
            .format(self.widget.name, old_uids, uids))

        # Delete objects that were removed
        if old_uids:
            removed_uids = set(old_uids) - set(uids)
            if removed_uids:
                logger.info("Deleting removed UIDs: {}".format(removed_uids))
                self.delete_removed_files(context, removed_uids)

        # Ensure all UIDs are strings (avoid "Wrong containing type" error)
        return [str(uid) for uid in uids] if uids else []

    def delete_removed_files(self, container, uids):
        """Delete File/Image objects that were removed from the field

        :param container: The parent container
        :param uids: Set of UIDs to delete
        """
        if not uids:
            return

        # Remove the files using the `IMultiUploadFileRemover` adapter
        remover = getAdapter(container, IMultiUploadFileRemover)
        remover.remove(uids)


@adapter(IUIDReferenceField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def MultiUploadWidgetFactory(field, request):
    """Factory for the multi-upload widget

    Only applies to IUIDReferenceField fields that need to store
    multiple file/image UIDs.
    """
    return FieldWidget(field, MultiUploadWidget(request))
