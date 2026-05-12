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
from senaite.core.interfaces import IMultiUploadWidget
from senaite.core.interfaces import ISenaiteFormLayer
from senaite.core.schema.interfaces import IMultiUploadField
from senaite.core.schema.interfaces import IUIDReferenceField
from senaite.core.z3cform.widgets.uidreference.widget import UIDReferenceWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
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

        # Use the @@download view
        if portal_type == "SimpleFile":
            return "{}/@@download/file".format(url)
        elif portal_type == "SimpleImage":
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
        return list(filter(api.is_uid, value))

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

    def is_add_form(self):
        """Check if we are in an add form

        :returns: True if in add form, False if in edit form
        """
        # Check if the parent form implements IAddForm
        form = getattr(self, "form", None)
        if form is None:
            return False

        # Check for z3c.form IAddForm interface
        return IAddForm.providedBy(form)

    def extract(self, default=None):
        """Extract uploaded files from request

        Returns current field value in edit forms or empty list in add forms.
        Upload UUIDs remain in request for event subscriber processing.

        :param default: Default value if extraction fails
        :returns: List of UIDs
        """
        logger.info("="*80)
        logger.info("extract() called for field '{}'".format(self.name))

        # In add forms, return empty list (no existing values)
        if self.is_add_form():
            logger.info("extract for '{}': add form, returning []".format(
                self.name))
            return []

        # In edit forms, get current field value from context
        field_name = self.field.__name__
        try:
            current_value = getattr(self.context, field_name, [])
            if current_value is None:
                current_value = []
            logger.info("extract for '{}': edit form, value={}".format(
                self.name, current_value))
            return list(filter(api.is_uid, current_value))
        except (AttributeError, TypeError) as e:
            logger.warning("extract for '{}': error getting value: {}".format(
                self.name, str(e)))
            return []


@adapter(IMultiUploadField, IMultiUploadWidget)
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

        The extract() method returned a list of UIDs.

        :param value: List of UIDs from extract()
        :returns: List of UIDs
        """
        # Value from extract() is already a list of UIDs
        if value is None:
            result = []
        else:
            result = list(value)

        logger.info(
            "toFieldValue for field '{}': result={}"
            .format(self.widget.name, result))

        # Ensure all values are strings (avoid "Wrong containing type" error)
        return [str(v) for v in result] if result else []


@adapter(IUIDReferenceField, ISenaiteFormLayer)
@implementer(IFieldWidget)
def MultiUploadWidgetFactory(field, request):
    """Factory for the multi-upload widget

    Only applies to IUIDReferenceField fields that need to store
    multiple file/image UIDs.
    """
    return FieldWidget(field, MultiUploadWidget(request))
