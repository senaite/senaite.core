# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.interface import implements


class IBeforeUpgradeStepEvent(Interface):
    """An event fired before the upgrade step started
    """


class IAfterUpgradeStepEvent(Interface):
    """An event fired after the upgrade step completed
    """


class BeforeUpgradeStepEvent(object):
    implements(IBeforeUpgradeStepEvent)

    def __init__(self, context):
        self.context = context


class AfterUpgradeStepEvent(object):
    implements(IAfterUpgradeStepEvent)

    def __init__(self, context):
        self.context = context
