# -*- coding: utf-8 -*-

from zope.interface import implementer
from zope.container.interfaces import INameChooser
from senaite.core.idserver import generateUniqueId


@implementer(INameChooser)
class IDChooser(object):
    """Choose a vaild ID for the given container and object
    """
    def __init__(self, context):
        self.context = context

    def chooseID(self, name, object):
        return self.chooseName(name, object)

    def checkName(self, name, object):
        return True

    def chooseName(self, name, object):
        """Choose a valid ID for the given object
        """
        return generateUniqueId(object, container=self.context)
