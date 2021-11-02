# -*- coding: utf-8 -*-

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.Archetypes import utils


def isFactoryContained(obj):
    """Are we inside the portal_factory?
    """
    if obj.isTemporary():
        return True
    parent = aq_parent(aq_inner(obj))
    if parent is None:
        # We don't have enough context to know where we are
        return False
    meta_type = getattr(aq_base(parent), "meta_type", "")
    return meta_type == "TempFolder"


# https://pypi.org/project/collective.monkeypatcher/#patching-module-level-functions 
utils.isFactoryContained = isFactoryContained
