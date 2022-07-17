# -*- coding: utf-8 -*-

from zope.interface import implementer
from zope.interface.interfaces import IObjectEvent


class IUIDReferenceCreatedEvent(IObjectEvent):
    """An event fired after a reference between two objects was cretated
    """


class IUIDReferenceDestroyedEvent(IObjectEvent):
    """An event fired after a reference between two objects was destroyed
    """


@implementer(IUIDReferenceCreatedEvent)
class UIDReferenceCreated(object):

    def __init__(self, field, source, target):
        """Reference Created Event

        :param field: The field on the source object
        :param source: The context object holding the UID reference field
        :param target: The context object being referenced
        """
        self.field = field
        self.source = source
        self.target = target

        # See IObjectEvent
        # -> Allow to define an event subscriber for a custom type
        self.object = source


@implementer(IUIDReferenceDestroyedEvent)
class UIDReferenceDestroyed(object):

    def __init__(self, field, source, target):
        """Reference Destroyed Event

        :param field: The field on the source object
        :param source: The context object holding the UID reference field
        :param target: The context object being referenced
        """
        self.field = field
        self.source = source
        self.target = target

        # See IObjectEvent
        # -> Allow to define an event subscriber for a custom type
        self.object = source
