# -*- coding: utf-8 -*-

from senaite.core.idserver import generateUniqueId
from senaite.core.interfaces import IAutoGenerateID
from zope.container.contained import NameChooser
from zope.container.interfaces import INameChooser
from zope.interface import implementer
from plone.app.content.namechooser import NormalizingNameChooser


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
        if not IAutoGenerateID.providedBy(object):
            default_chooser = NormalizingNameChooser(self.context)
            return default_chooser.chooseName(name, object)
        return generateUniqueId(object, container=self.context)
