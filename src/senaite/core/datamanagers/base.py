# -*- coding: utf-8 -*-

from bika.lims.api.security import check_permission
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from senaite.core.interfaces.datamanager import IDataManager
from zope.interface import implementer


@implementer(IDataManager)
class DataManager(object):
    """Data manager base class."""

    def __init__(self, context):
        self.context = context

    def get(self, name):
        raise NotImplementedError("Must be implemented by subclass")

    def query(self, name, default=None):
        try:
            return self.get(name)
        except AttributeError:
            return default

    def set(self, name, value):
        raise NotImplementedError("Must be implemented by subclass")

    def can_access(self):
        return check_permission(View, self.context)

    def can_write(self):
        return check_permission(ModifyPortalContent, self.context)


@implementer(IDataManager)
class FieldDataManager(DataManager):
    """Base class for field managers
    """

    def __init__(self, context, request, field):
        self.context = context
        self.request = request
        self.field = field

    def get(self):
        raise NotImplementedError("Must be implemented by subclass")

    def query(self, default=None):
        try:
            return self.field.get(self.context)
        except AttributeError:
            return default

    def set(self, value):
        raise NotImplementedError("Must be implemented by subclass")

    def can_access(self):
        return check_permission(View, self.context)

    def can_write(self):
        return check_permission(ModifyPortalContent, self.context)
