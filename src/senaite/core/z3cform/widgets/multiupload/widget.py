# -*- coding: utf-8 -*-

import json

from bika.lims import api
from bika.lims import logger
from senaite.core.interfaces import IMultiUploadFileCreator
from senaite.core.interfaces import IMultiUploadFileRemover
from senaite.core.interfaces import IMultiUploadWidget
from senaite.core.interfaces import ISenaiteFormLayer
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
                logger.error("Could not retrieve object for UID: {}".format(uid))
                continue

        return existing_files

    def get_data_attributes(self):
        """Return data attributes for the React widget"""
        existing_files = self.get_existing_files_data()

        return {
            "fieldname": self.name,
            "portal_url": self.portal_url,
            "context_url": self.context_url,
            "endpoint": "@@multiupload_handler",
            "max_filesize": 10485760,  # 10MB default
            "accepted_types": {},  # Accept all file types by default
            "existing_files": existing_files,
        }

    def render_data_attributes(self):
        """Render data attributes as HTML string"""
        attrs = []
        for key, value in self.get_data_attributes().items():
            json_value = json.dumps(value)
            # Escape quotes for HTML attribute
            json_value = json_value.replace('"', '&quot;')
            attrs.append('data-{}="{}"'.format(key, json_value))
        return " ".join(attrs)

    def extract(self, default=None):
        """Extract uploaded files from request
        """
        # Get the JSON data from the hidden field
        data_field = self.name + '.data'
        data = self.request.form.get(data_field, None)

        if data:
            try:
                # Parse the JSON data containing file IDs
                return json.loads(data)
            except (ValueError, TypeError):
                pass

        return default


@adapter(IMultiUploadWidget)
@implementer(IDataConverter)
class MultiUploadDataConverter(BaseDataConverter):
    """Data converter for multi-upload widget

    Converts between widget values (upload IDs) and field values (UIDs).
    Creates File/Image objects from uploads and returns their UIDs.
    Deletes File/Image objects that were removed from the field.
    """

    def toWidgetValue(self, value):
        """Convert from field value (UIDs) to widget value

        :param value: Tuple of UIDs
        :returns: Tuple of UIDs
        """
        if value is None:
            return ()
        return value

    def toFieldValue(self, value):
        """Convert from widget value (upload IDs) to field value (UIDs)

        Creates File/Image objects for uploaded files and returns their UIDs.
        Also handles deletion of removed files.

        :param value: Upload IDs from the widget (JSON)
        :returns: Tuple of UIDs
        """
        # Get the field and context
        field = self.field
        context = self.widget.context

        # Get current field value (old UIDs before form processing)
        old_value = field.get(context) if hasattr(field, 'get') else ()
        old_uids = list(old_value) if old_value else []

        # Get existing UIDs from the main field (maintained by React)
        main_value = self.widget.request.form.get(self.widget.name, "")
        existing_uids = []
        if main_value:
            if isinstance(main_value, str):
                existing_uids = [uid.strip() for uid in main_value.split("\r\n") if uid.strip()]
            elif isinstance(main_value, (list, tuple)):
                existing_uids = [uid for uid in main_value if uid]

        logger.info("toFieldValue for field '{}': old_uids={}, existing_uids={}".format(
            self.widget.name, old_uids, existing_uids))

        # Start with existing UIDs
        uids = list(existing_uids)

        # Get upload IDs from the .data field
        upload_ids = []
        if value:
            upload_ids = value if isinstance(value, (list, tuple)) else []

        logger.info("toFieldValue for field '{}': upload_ids={}".format(
            self.widget.name, upload_ids))

        # Get session and uploaded files
        session = self.widget.request.SESSION
        uploaded_files = session.get("multiupload_files", {})

        # Track created UIDs to handle multiple calls
        created_uids_key = "multiupload_created_uids"
        created_uids_map = session.get(created_uids_key, {})

        # Create File/Image objects for each uploaded file
        for upload_id in upload_ids:
            # Check if we already created an object for this upload_id
            if upload_id in created_uids_map:
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
                        (context, field),
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

                except Exception as e:
                    import traceback
                    logger.error(u"Error creating object {}: {}".format(
                        filename, api.safe_unicode(str(e))))
                    logger.error(traceback.format_exc())
                    continue
            else:
                logger.warning("Upload ID {} not found in session, skipping".format(
                    upload_id))

        logger.info("toFieldValue for field '{}': final UIDs={}".format(
            self.widget.name, uids))

        # Delete File/Image objects that were removed
        if old_uids:
            removed_uids = set(old_uids) - set(uids)
            logger.info("Removed UIDs: {}".format(removed_uids))
            if removed_uids:
                self.delete_removed_files(context, removed_uids)

        return tuple(uids)

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


@adapter(ITuple, ISenaiteFormLayer)
@implementer(IFieldWidget)
def MultiUploadWidgetFactory(field, request):
    """Factory for the multi-upload widget"""
    return FieldWidget(field, MultiUploadWidget(request))
