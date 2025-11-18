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
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from Products.Archetypes.Registry import registerWidget
from senaite.core.browser.widgets.referencewidget import ReferenceWidget


class MultiFileUploadWidget(ReferenceWidget):
    """Widget for uploading files that creates File/Image objects
    and stores their UIDs as references.

    This widget integrates with the React multiupload widget to:
    1. Accept file uploads
    2. Create File or Image objects
    3. Store them in the parent container
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
            "data-id": field.getName(),
            "data-name": field.getName(),
            "data-endpoint": endpoint,
            "data-portal_url": portal_url,
            "data-context_url": context_url,
            "data-max_filesize": max_filesize,
            "data-accepted_types": json.dumps(accepted_types),
        }

        return attributes

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """Process form data and create File/Image objects from uploads

        This method:
        1. Gets uploaded file IDs from the session (stored by multiupload handler)
        2. Creates File or Image objects based on content type
        3. Returns the list of UIDs to be stored in the field
        """
        field_name = field.getName()

        # Get the JSON data from the hidden field
        data_field = field_name + ".data"
        data = form.get(data_field, None)

        if not data:
            # Return existing value if no new uploads
            existing = field.get(instance)
            if existing:
                if isinstance(existing, (list, tuple)):
                    return existing, {}
                return [existing], {}
            return [], {}

        try:
            # Parse the JSON data containing upload IDs
            upload_ids = json.loads(data)
        except (ValueError, TypeError):
            logger.error("Invalid JSON data for field {}".format(field_name))
            return [], {}

        # Get uploaded files from session
        session = instance.REQUEST.SESSION
        uploaded_files = session.get("multiupload_files", {})

        # Get existing UIDs to preserve them
        existing_uids = []
        existing = field.get(instance)
        if existing:
            if isinstance(existing, (list, tuple)):
                existing_uids = [api.get_uid(obj) for obj in existing if api.is_object(obj)]
            elif api.is_object(existing):
                existing_uids = [api.get_uid(existing)]

        uids = list(existing_uids)

        # Create File/Image objects for each uploaded file
        for upload_id in upload_ids:
            if upload_id in uploaded_files:
                file_data = uploaded_files[upload_id]

                data = file_data["data"]
                filename = file_data["filename"]
                content_type = file_data["content_type"]
                is_image = content_type.startswith("image/")

                # Create NamedBlobFile or NamedBlobImage from stored data
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
                    # The blob is passed directly
                    obj = createContentInContainer(
                        instance,
                        portal_type,
                        title=filename,
                        file=blob,
                        checkConstraints=False,
                    )

                    # Make it referenceable
                    obj.reindexObject()

                    # Get UID
                    uid = api.get_uid(obj)
                    uids.append(uid)

                    logger.info("Created {} object {} with UID {}".format(
                        portal_type, filename, uid))

                except Exception as e:
                    logger.error("Error creating {} object: {}".format(
                        portal_type, str(e)))
                    continue

        # Clean up session
        if upload_ids:
            for upload_id in upload_ids:
                uploaded_files.pop(upload_id, None)
            session["multiupload_files"] = uploaded_files

        # Handle multi-valued vs single-valued
        multi_valued = getattr(field, "multiValued", False)
        if not multi_valued:
            return uids[0] if uids else "", {}

        return uids, {}


registerWidget(MultiFileUploadWidget,
               title="Multi File Upload Widget",
               description="Widget for uploading files as File/Image objects with UID references",
               used_for=("bika.lims.browser.fields.UIDReferenceField",))

# Backward compatibility alias
UIDReferenceFileWidget = MultiFileUploadWidget
