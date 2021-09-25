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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import json
import six

from datetime import datetime
from mimetypes import guess_type

from bika.lims import api
from bika.lims import logger
from bika.lims.interfaces.field import IUIDReferenceField
from DateTime import DateTime
from plone.app.blob.interfaces import IBlobField
from plone.app.textfield.interfaces import IRichText
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile.interfaces import INamedField
from Products.Archetypes.interfaces import IBaseObject
from Products.Archetypes.interfaces import IDateTimeField
from Products.Archetypes.interfaces import IField
from Products.Archetypes.interfaces import IFileField
from Products.Archetypes.interfaces import IReferenceField
from Products.Archetypes.interfaces import ITextField
from Products.CMFPlone.utils import safe_unicode
from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.utils import NodeAdapterBase
from zope.component import adapts
from zope.interface import implements
from zope.schema.interfaces import IDatetime
from zope.schema.interfaces import IField as ISchemaField

from .config import SITE_ID
from .interfaces import IFieldNode
from .interfaces import IRecordField

SKIP_FIELDS = [
    "id",
    "rights",
]


class ATFieldNodeAdapter(NodeAdapterBase):
    """Node im- and exporter for AT Fields.
    """
    implements(IFieldNode)
    adapts(IBaseObject, IField, ISetupEnviron)

    el = "field"

    def __init__(self, context, field, environ):
        super(ATFieldNodeAdapter, self).__init__(context, environ)
        self.field = field

    def set_field_value(self, value, **kw):
        """Set the field value
        """
        # logger.info("Set: {} -> {}".format(self.field.getName(), value))
        return self.field.set(self.context, value, **kw)

    def get_field_value(self):
        """Get the field value
        """
        return self.field.get(self.context)

    def get_json_value(self):
        """JSON converted field value
        """
        value = self.get_field_value()
        try:
            # Always handle the value as unicode
            return json.dumps(safe_unicode(value))
        except TypeError:
            logger.error(
                "ParseError: '{}.{} ('{}')' is not JSON serializable!".format(
                    self.context.getId(), self.field.getName(), repr(value)))
            return ""

    def parse_json_value(self, value):
        return json.loads(value)

    def get_node_value(self, value):
        """Convert the field value to a XML node
        """
        node = self._doc.createElement(self.el)
        node.setAttribute("name", self.field.getName())
        child = self._doc.createTextNode(value)
        node.appendChild(child)
        return node

    def set_node_value(self, node):
        value = self.parse_json_value(node.nodeValue)
        # encode unicodes to UTF8
        if isinstance(value, unicode):
            value = value.encode("utf8")
        self.set_field_value(value)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        value = self.get_json_value()
        return self.get_node_value(value)

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.field.getName() in SKIP_FIELDS:
            return
        child = node.firstChild
        if child is None:
            return
        if child.nodeName != "#text":
            logger.warning("No textnode found!")
            return False
        self.set_node_value(child)

    node = property(_exportNode, _importNode)


class DXFieldNodeAdapter(ATFieldNodeAdapter):
    """Node im- and exporter for DX Fields.
    """
    implements(IFieldNode)
    adapts(IDexterityContent, ISchemaField, ISetupEnviron)

    def __init__(self, context, field, environ):
        super(DXFieldNodeAdapter, self).__init__(context, field, environ)
        self.field = field


class ATTextFieldNodeAdapter(ATFieldNodeAdapter):
    """Import/Export Text
    """
    adapts(IBaseObject, ITextField, ISetupEnviron)


class ATFileFieldNodeAdapter(ATFieldNodeAdapter):
    """Import/Export Files/Images
    """
    adapts(IBaseObject, IFileField, ISetupEnviron)

    def set_node_value(self, node):
        filename = node.nodeValue
        filepath = "/".join([self.get_archive_path(), filename])
        data = self.get_file_data(filepath)
        self.set_field_value(data, filename=filename)

    def get_archive_path(self):
        """Get the unified archive path
        """
        site = self.environ.getSite()
        site_path = api.get_path(site)
        obj_path = api.get_path(self.context)
        return obj_path.replace(site_path, SITE_ID, 1)

    def get_file_data(self, path):
        """Return the file data from the archive path
        """
        return self.environ.readDataFile(path)

    def get_content_type(self, content, default="application/octet-stream"):
        """Returns the content type of the object
        """
        return getattr(content, "content_type", default)

    def get_json_value(self):
        """Returns the filename
        """
        value = self.get_field_value()

        if isinstance(value, six.string_types):
            return value

        filename = safe_unicode(value.filename) or ""
        data = value.data
        if filename and data:
            path = self.get_archive_path()
            content_type = self.get_content_type(value)
            self.environ.writeDataFile(filename, str(data), content_type, path)
        return filename


class ATBlobFileFieldNodeAdapter(ATFileFieldNodeAdapter):
    """Import/Export AT Files/Images
    """
    adapts(IBaseObject, IBlobField, ISetupEnviron)


class DXNamedFileFieldNodeAdapter(ATBlobFileFieldNodeAdapter):
    """Import/Export DX Files/Images
    """
    adapts(IDexterityContent, INamedField, ISetupEnviron)

    def get_content_type(self, content, default="application/octet-stream"):
        """Returns the content type of the object
        """
        return getattr(content, "contentType", default)

    def set_node_value(self, node):
        filename = node.nodeValue
        filepath = "/".join([self.get_archive_path(), filename])
        data = self.get_file_data(filepath)
        mime_type, encoding = guess_type(filename)
        self.set_field_value(data, filename=filename, content_type=mime_type)

    def set_field_value(self, value, **kw):
        """Set the field value
        """
        # logger.info("Set: {} -> {}".format(self.field.getName(), value))
        data = value
        if not data:
            logger.error("Can not set empty file contents")
            return
        filename = kw.get("filename", "")
        contentType = kw.get("mimetype") or kw.get("content_type")
        value = self.field._type(
            data=data, contentType=contentType, filename=filename)
        self.field.set(self.context, value)


class ATDateTimeFieldNodeAdapter(ATFieldNodeAdapter):
    """Import/Export Date Fields
    """
    adapts(IBaseObject, IDateTimeField, ISetupEnviron)

    def get_json_value(self):
        """Returns the date as ISO string
        """
        value = self.field.get(self.context)
        if not isinstance(value, DateTime):
            return ""
        return value.ISO()

    def parse_json_value(self, value):
        if not value:
            return None
        return DateTime(value)


class DXDateTimeFieldNodeAdapter(ATFieldNodeAdapter):
    """Import/Export Date Fields
    """
    adapts(IDexterityContent, IDatetime, ISetupEnviron)

    def get_json_value(self):
        """Returns the date as ISO string
        """
        value = self.field.get(self.context)
        if not isinstance(value, datetime):
            return ""
        return value.isoformat()

    def parse_json_value(self, value):
        if not value:
            return None
        dt = api.to_date(value)
        return dt.asdatetime()


class ATReferenceFieldNodeAdapter(ATFieldNodeAdapter):
    """Import/Export UID Reference Fields
    """
    adapts(IBaseObject, IReferenceField, ISetupEnviron)

    def get_json_value(self):
        """Returns the date as ISO string
        """
        value = self.field.get(self.context)
        if api.is_object(value):
            value = api.get_uid(value)
        elif isinstance(value, list):
            value = map(api.get_uid, value)
        else:
            value = ""
        return json.dumps(value)


class ATUIDReferenceFieldNodeAdapter(ATReferenceFieldNodeAdapter):
    """Import/Export UID Reference Fields
    """
    adapts(IBaseObject, IUIDReferenceField, ISetupEnviron)


class ATRecordFieldNodeAdapter(ATFieldNodeAdapter):
    """Import/Export Records Fields
    """
    adapts(IBaseObject, IRecordField, ISetupEnviron)


class ATRichTextFieldNodeAdapter(ATFieldNodeAdapter):
    """Node im- and exporter for AT RichText fields.
    """
    implements(IFieldNode)
    adapts(IBaseObject, IRichText, ISetupEnviron)

    def get_field_value(self):
        """Get the field value
        """
        value = self.field.get(self.context)
        if not value:
            return ""
        try:
            return value.raw
        except AttributeError as e:
            logger.info("Imported value has no Attribute 'raw' {}".format(str(e)))
            return value


class DXRichTextFieldNodeAdapter(ATRichTextFieldNodeAdapter):
    """Node im- and exporter for AT RichText fields.
    """
    implements(IFieldNode)
    adapts(IDexterityContent, IRichText, ISetupEnviron)
