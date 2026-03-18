# -*- coding: utf-8 -*-

from zope.interface import implementer
from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


class IAfterAPICreatedObjectEvent(IObjectModifiedEvent):
    """An object is being initialised, i.e. populated for the first time
    """


@implementer(IAfterAPICreatedObjectEvent)
class AfterAPICreatedObjectEvent(ObjectModifiedEvent):
    """An object is being initialised, i.e. populated for the first time
    """
