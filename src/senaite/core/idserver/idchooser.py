# -*- coding: utf-8 -*-

from bika.lims import api
from plone.app.content.namechooser import NormalizingNameChooser
from senaite.core.idserver import generateUniqueId
from senaite.core.interfaces import IAutoGenerateID
from zope.container.interfaces import INameChooser

from zope.interface import implementer


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
        if api.is_at_type(object):
            return self.chooseATName(name, object)
        return self.chooseDXName(name, object)

    def chooseATName(self, name, object):
        return generateUniqueId(object, container=self.context)

    def chooseDXName(self, name, object):
        if not IAutoGenerateID.providedBy(object):
            return self.chooseDefaultName(name, object)
        return generateUniqueId(object, container=self.context)

    def chooseDefaultName(self, name, object):
        default_chooser = NormalizingNameChooser(self.context)
        return default_chooser.chooseName(name, object)
