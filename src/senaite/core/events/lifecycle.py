# -*- coding: utf-8 -*-


from zope.interface import implementer
from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


class IObjectInitializedEvent(IObjectModifiedEvent):
    """An object is being initialised, i.e. populated for the first time
    """


@implementer(IObjectInitializedEvent)
class ObjectInitializedEvent(ObjectModifiedEvent):
    """An object is being initialised, i.e. populated for the first time
    """
