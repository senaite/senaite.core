# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.interface import implements


class IRemarksAddedEvent(Interface):
    """Remarks Added Event
    """


class RemarksAddedEvent(object):
    implements(IRemarksAddedEvent)

    def __init__(self, context, history):
        self.context = context
        self.history = history
