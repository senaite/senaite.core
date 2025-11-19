# -*- coding: utf-8 -*-

import json

from bika.lims import api
from bika.lims import logger
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from senaite.core.interfaces import IMultiUploadWidget
from senaite.core.interfaces import ISenaiteFormLayer
from z3c.form.browser import widget
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementer_only
from zope.schema.interfaces import ITuple


@implementer_only(IMultiUploadWidget)
class MultiUploadWidget(widget.HTMLFormElement, Widget):
    """Multi-file upload widget using React and react-dropzone
    """

    klass = u"multi-upload-widget"
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
                portal_type = api.get_portal_type(obj)
                file_data = {
                    "uid": uid,
                    "name": api.get_title(obj),
                    "url": self.get_download_url(obj),
                    "type": portal_type,
                }

                # Try to get file size if available
                # Image objects use 'image' field, File objects use 'file' field
                field_name = "image" if portal_type == "Image" else "file"
                file_obj = getattr(obj, field_name, None)
                if file_obj and hasattr(file_obj, "size"):
                    file_data["size"] = file_obj.size
                elif file_obj and hasattr(file_obj, "getSize"):
                    file_data["size"] = file_obj.getSize()
                else:
                    file_data["size"] = 0

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
                is_image = content_type.startswith("image/")

                # Create NamedBlobFile or NamedBlobImage
                if is_image:
                    blob = NamedBlobImage(
                        data=data,
                        filename=filename,
                        contentType=content_type
                    )
                else:
                    blob = NamedBlobFile(
                        data=data,
                        filename=filename,
                        contentType=content_type
                    )

                # Determine portal type
                portal_type = "Image" if is_image else "File"

                try:
                    # Create the object in the parent container
                    # Note: Image objects use 'image' field, File objects use 'file' field
                    field_name = "image" if is_image else "file"
                    kwargs = {
                        field_name: blob,
                        "title": filename,
                        "checkConstraints": False,
                    }
                    obj = createContentInContainer(
                        context,
                        portal_type,
                        **kwargs
                    )

                    # Reindex to update catalogs
                    obj.reindexObject()

                    # Get UID
                    uid = api.get_uid(obj)
                    uids.append(uid)

                    # Store the UID for this upload_id in session
                    created_uids_map[upload_id] = uid
                    session[created_uids_key] = created_uids_map

                    logger.info(u"Created {} object {} with UID {}".format(
                        portal_type, filename, uid))

                except Exception as e:
                    import traceback
                    logger.error(u"Error creating {} object {}: {}".format(
                        portal_type, filename, api.safe_unicode(str(e))))
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
                self._delete_removed_files(context, removed_uids)

        return tuple(uids)

    def _delete_removed_files(self, container, uids):
        """Delete File/Image objects that were removed from the field

        :param container: The parent container
        :param uids: Set of UIDs to delete
        """
        if not uids:
            return

        logger.info("Deleting {} removed file(s) from {}".format(
            len(uids), api.get_path(container)))

        # Use privileged context to delete files
        with api.security.as_privileged_user():
            for uid in uids:
                try:
                    obj = api.get_object(uid)
                    parent = api.get_parent(obj)

                    # Verify the object lives in this container
                    if parent != container:
                        logger.warning(
                            "Skipping deletion of {}: not in container "
                            "(parent: {}, expected: {})".format(
                                uid, api.get_path(parent), api.get_path(container)))
                        continue

                    # Verify it's a File or Image
                    if api.get_portal_type(obj) not in ["File", "Image"]:
                        logger.warning(
                            "Skipping deletion of {}: not a File/Image "
                            "(type: {})".format(uid, api.get_portal_type(obj)))
                        continue

                    # Store info before deletion for logging
                    obj_title = api.get_title(obj)
                    obj_type = api.get_portal_type(obj)
                    obj_path = api.get_path(obj)

                    # Delete the object
                    api.delete(obj)
                    logger.info(u"Deleted {} object: {} (was at: {})".format(
                        obj_type, api.safe_unicode(obj_title), obj_path))

                except api.APIError as e:
                    logger.error("Error deleting object {}: {}".format(uid, str(e)))
                    import traceback
                    logger.error(traceback.format_exc())
                    continue
                except Exception as e:
                    logger.error("Unexpected error deleting object {}: {}".format(
                        uid, str(e)))
                    import traceback
                    logger.error(traceback.format_exc())
                    continue


@adapter(ITuple, ISenaiteFormLayer)
@implementer(IFieldWidget)
def MultiUploadWidgetFactory(field, request):
    """Factory for the multi-upload widget"""
    return FieldWidget(field, MultiUploadWidget(request))
