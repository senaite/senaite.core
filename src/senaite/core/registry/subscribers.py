# -*- coding: utf-8 -*-

from bika.lims import api
from Products.CMFPlone.utils import classDoesNotImplement
from Products.CMFPlone.utils import classImplements
from senaite.core.interfaces import ICanHaveLabels
from plone.dexterity.utils import resolveDottedName
from Products.Archetypes.atapi import listTypes


def get_klass(portal_type):
    portal_types = api.get_tool("portal_types")
    fti = portal_types.getTypeInfo(portal_type)

    if fti.product:
        at_types = listTypes(fti.product)
        for t in at_types:
            if not t.get("portal_type") == portal_type:
                continue
            return t.get("klass")
    else:
        return resolveDottedName(fti.klass)


def update_label_registry(object, event):
    # get the types that support labels directly
    enabled_types = object.label_enabled_portal_types
    plone_utils = api.get_tool("plone_utils")
    friendly_types = plone_utils.getUserFriendlyTypes()
    for portal_type in friendly_types:
        klass = get_klass(portal_type)
        if portal_type not in enabled_types:
            classDoesNotImplement(klass, ICanHaveLabels)
        else:
            classImplements(klass, ICanHaveLabels)
