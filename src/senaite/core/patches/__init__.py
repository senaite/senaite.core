# -*- coding: utf-8 -*-

from bika.lims import api
from Products.Archetypes import utils


def isFactoryContained(obj):
    """Are we inside the portal_factory?
    """
    return api.is_temporary(obj)


# https://pypi.org/project/collective.monkeypatcher/#patching-module-level-functions 
utils.isFactoryContained = isFactoryContained
