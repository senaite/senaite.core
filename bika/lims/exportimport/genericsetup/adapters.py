# -*- coding: utf-8 -*-

import json

from bika.lims import api
from bika.lims import logger
from bika.lims.interfaces.field import IUIDReferenceField
from DateTime import DateTime
from plone.app.blob.interfaces import IBlobField
# from Products.Archetypes.interfaces import IStringField
from Products.Archetypes.interfaces import IBaseObject
from Products.Archetypes.interfaces import IDateTimeField
from Products.Archetypes.interfaces import IField
from Products.Archetypes.interfaces import IFileField
from Products.Archetypes.interfaces import IReferenceField
from Products.Archetypes.interfaces import ITextField
from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.utils import NodeAdapterBase
from zope.component import adapts

SKIP_FIELDS = [
    "id",
    "created",
    "Creator",
    "modified",
    "rights",
]


class ATFieldNodeAdapter(NodeAdapterBase):
    """Node im- and exporter for Fields.
    """
    adapts(IBaseObject, IField, ISetupEnviron)

    def __init__(self, context, field, environ):
        super(ATFieldNodeAdapter, self).__init__(context, environ)
        self.field = field

    def get_field_name(self):
        return self.field.getName()

    def get_field_value(self):
        value = self.field.get(self.context)
        try:
            return json.dumps(value)
        except TypeError:
            logger.warning(
                "ParseError: '{}.{} ('{}') -> {}' is not JSON serializable!"
                .format(self.context.getId(), self.field.getName(),
                        self.field.type, repr(value)))
            return ""

    def parse_value(self, value):
        value = json.loads(value)
        if self.field.getName() == "id":
            value = str(value)
        return value

    def set_field(self, value, **kw):
        """Set the field value
        """
        logger.info(
            "Set {} -> {}".format(self.field.getName(), repr(value)))
        self.field.set(self.context, value, **kw)

    def make_field_node(self, value):
        node = self._doc.createElement("field")
        node.setAttribute("name", self.field.getName())
        child = self._doc.createTextNode(value)
        node.appendChild(child)
        return node

    def import_node(self, node):
        value = self.parse_value(node.nodeValue)
        self.set_field(value)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        value = self.get_field_value()
        return self.make_field_node(value)

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.get_field_name() in SKIP_FIELDS:
            return
        child = node.firstChild
        if child is None:
            return
        if child.nodeName != "#text":
            logger.warning("No textnode found!")
            return False
        self.import_node(child)

    node = property(_exportNode, _importNode)


class ATTextFieldNodeAdapter(ATFieldNodeAdapter):
    """Import/Export Text
    """
    adapts(IBaseObject, ITextField, ISetupEnviron)


class ATFileFieldNodeAdapter(ATFieldNodeAdapter):
    """Import/Export Files/Images
    """
    adapts(IBaseObject, IFileField, ISetupEnviron)

    def import_node(self, node):
        value = node.nodeValue
        filename = node.nodeValue
        data = self.parse_value(value)
        self.set_field(data, filename=filename)

    def get_path(self):
        """Get the relative path
        """
        site = self.environ.getSite()
        site_path = api.get_path(site)
        obj_path = api.get_path(self.context)
        return obj_path.lstrip(site_path)

    def get_field_value(self):
        """Returns the filename
        """
        value = self.field.get(self.context)

        if isinstance(value, basestring):
            return value

        filename = value.filename or ""
        data = value.data
        if filename and data:
            path = self.get_path()
            content_type = value.content_type
            self.environ.writeDataFile(filename, str(data), content_type, path)
        return filename

    def parse_value(self, value):
        filename = "/".join([self.get_path(), value])
        data = self.environ.readDataFile(filename)
        return data

    def set_field(self, value, **kw):
        """Set the field value
        """
        logger.info("Set file field {}".format(self.get_field_name()))
        self.field.set(self.context, value, **kw)


class BlobFileFieldNodeAdapter(ATFileFieldNodeAdapter):
    """Import/Export Files/Images
    """
    adapts(IBaseObject, IBlobField, ISetupEnviron)


class ATDateTimeFieldNodeAdapter(ATFieldNodeAdapter):
    """Import/Export Date Fields
    """
    adapts(IBaseObject, IDateTimeField, ISetupEnviron)

    def get_field_value(self):
        """Returns the date as ISO string
        """
        value = self.field.get(self.context)
        if not isinstance(value, DateTime):
            return ""
        return value.ISO()

    def parse_value(self, value):
        if not value:
            return None
        return DateTime(value)


class ATReferenceFieldNodeAdapter(ATFieldNodeAdapter):
    """Import/Export UID Reference Fields
    """
    adapts(IBaseObject, IReferenceField, ISetupEnviron)

    def get_field_value(self):
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

    def parse_value(self, value):
        value = json.loads(value)
        if value and not isinstance(value, list):
            value = [value]
        if not value:
            return []
        return map(lambda uid: self.uid_map.get(uid), value)


class ATUIDReferenceFieldNodeAdapter(ATReferenceFieldNodeAdapter):
    """Import/Export UID Reference Fields
    """
    adapts(IBaseObject, IUIDReferenceField, ISetupEnviron)
