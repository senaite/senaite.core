# -*- coding: utf-8 -*-

from zope.interface import implementer
from zope.interface.interfaces import IObjectEvent
from zope.interface.interfaces import ObjectEvent


class IAfterAPICreatedObjectEvent(IObjectEvent):
    """An object has been created using api.create"""


@implementer(IAfterAPICreatedObjectEvent)
class AfterAPICreatedObjectEvent(ObjectEvent):
    """An object has been created using api.create"""
