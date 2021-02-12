# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from bika.lims import api
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
        if not self.can_access():
            raise Unauthorized("You are not allowed to access {}".format(
                api.get_id(self.context)))
        return getattr(self.context, name)

    def query(self, name, default=None):
        if not self.can_access():
            raise Unauthorized("You are not allowed to access {}".format(
                api.get_id(self.context)))
        return getattr(self.context, name, default)

    def set(self, name, value):
        if not self.can_access():
            raise Unauthorized("You are not allowed to modify {}".format(
                api.get_id(self.context)))
        return setattr(self.context, name, value)

    def can_access(self):
        return check_permission(View, self.context)

    def can_write(self):
        return check_permission(ModifyPortalContent, self.context)
