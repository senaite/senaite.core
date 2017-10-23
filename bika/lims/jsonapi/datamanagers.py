# -*- coding: utf-8 -*-

import Missing

from zope import interface

from AccessControl import Unauthorized
from AccessControl import getSecurityManager

from Products.CMFCore import permissions

from bika.lims import logger
from bika.lims.jsonapi import api
from bika.lims.jsonapi.interfaces import IDataManager
from bika.lims.jsonapi.interfaces import IFieldManager


class BaseDataManager(object):
    """Base Data Manager
    """
    interface.implements(IDataManager)

    def __init__(self, context):
        self.context = context

    def get(self, name):
        """Get the value for name
        """
        raise NotImplemented("Getter must be implemented by subclass")

    def set(self, name, value, **kw):
        """Set the value for name
        """
        raise NotImplemented("Setter must be implemented by subclass")

    def json_data(self, name, default=None):
        """Get a JSON compatible value of the field
        """
        raise NotImplemented("Get Info must be implemented by subclass")


class BrainDataManager(BaseDataManager):
    """Data Adapter for Catalog Brains
    """

    def get(self, name):
        """Get a JSON compatible structure for the named attribute
        """
        # read the attribute
        attr = getattr(self.context, name, None)
        if callable(attr):
            return attr()
        return attr

    def set(self, name, value, **kw):
        """Setter is not used for catalog brains
        """
        logger.warn("Setting is not allowed on catalog brains")

    def json_data(self, name, default=None):
        """Get a JSON compatible value of the field
        """
        value = self.get(name)
        if value is Missing.Value:
            return default
        return value


class PortalDataManager(BaseDataManager):
    """Data Adapter for the Portal Object
    """

    def get(self, name):
        """Get the value by name
        """

        # check read permission
        sm = getSecurityManager()
        permission = permissions.View
        if not sm.checkPermission(permission, self.context):
            raise Unauthorized("Not allowed to view the Plone portal")

        # read the attribute
        attr = getattr(self.context, name, None)
        if callable(attr):
            return attr()

        # XXX no really nice, but we want the portal to behave like an ordinary
        # content type. Therefore we need to inject the neccessary data.
        if name == "uid":
            return "0"
        if name == "path":
            return "/%s" % self.context.getId()
        return attr

    def set(self, name, value, **kw):
        """Set the attribute to the given value.

        The keyword arguments represent the other attribute values
        to integrate constraints to other values.
        """

        # check write permission
        sm = getSecurityManager()
        permission = permissions.ManagePortal
        if not sm.checkPermission(permission, self.context):
            raise Unauthorized("Not allowed to modify the Plone portal")

        # set the attribute
        if not hasattr(self.context, name):
            return False
        self.context[name] = value
        return True

    def json_data(self, name, default=None):
        """Get a JSON compatible structure for the named attribute
        """
        value = self.get(name)
        return value


class ATDataManager(BaseDataManager):
    """Data Adapter for AT Content Types
    """

    def get(self, name):
        """Get the value of the field by name
        """

        # fetch the field by name
        field = api.get_field(self.context, name)

        # bail out if we have no field
        if not field:
            return None

        # call the field adapter and set the value
        fieldmanager = IFieldManager(field)
        return fieldmanager.get(self.context)

    def set(self, name, value, **kw):
        """Set the field to the given value.

        The keyword arguments represent the other field values
        to integrate constraints to other values.
        """

        # fetch the field by name
        field = api.get_field(self.context, name)

        # bail out if we have no field
        if not field:
            return False

        # call the field adapter and set the value
        fieldmanager = IFieldManager(field)
        return fieldmanager.set(self.context, value, **kw)

    def json_data(self, name):
        """Get a JSON compatible structure for the named attribute
        """

        # fetch the field by name
        field = api.get_field(self.context, name)

        # bail out if we have no field
        if not field:
            return None

        fieldmanager = IFieldManager(field)
        return fieldmanager.json_data(self.context)


class DexterityDataManager(BaseDataManager):
    """Data Adapter for Dexterity Content Types
    """

    def get(self, name):
        """Get the value of the field by name
        """

        # Check the read permission of the context
        # XXX: This should be done on field level by the field manager adapter
        if not self.can_write():
            raise Unauthorized("You are not allowed to modify this content")

        # fetch the field by name
        field = api.get_field(self.context, name)

        # bail out if we have no field
        if field is None:
            return None

        # call the field adapter and set the value
        fieldmanager = IFieldManager(field)
        return fieldmanager.get(self.context)

    def set(self, name, value, **kw):
        """Set the field to the given value.

        The keyword arguments represent the other field values
        to integrate constraints to other values.
        """

        # Check the write permission of the context
        # XXX: This should be done on field level by the field manager adapter
        if not self.can_write():
            raise Unauthorized("You are not allowed to modify this content")

        # fetch the field by name
        field = api.get_field(self.context, name)

        # bail out if we have no field
        if not field:
            return False

        # call the field adapter and set the value
        fieldmanager = IFieldManager(field)
        return fieldmanager.set(self.context, value, **kw)

    def json_data(self, name):
        """Get a JSON compatible structure for the named attribute
        """

        # Check the write permission of the context
        # XXX: This should be done on field level by the field manager adapter
        if not self.can_write():
            raise Unauthorized("You are not allowed to modify this content")

        # fetch the field by name
        field = api.get_field(self.context, name)

        # bail out if we have no field
        if not field:
            return None

        fieldmanager = IFieldManager(field)
        return fieldmanager.json_data(self.context)

    def can_write(self):
        """Check if the field is writeable
        """
        sm = getSecurityManager()
        permission = permissions.ModifyPortalContent

        if not sm.checkPermission(permission, self.context):
            return False
        return True

    def can_read(self):
        """Check if the field is readable
        """
        sm = getSecurityManager()
        if not sm.checkPermission(permissions.View, self.context):
            return False
        return True
