# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims import logger
from bika.lims.api import create
from bika.lims.api import get_object
from bika.lims.api import get_senaite_setup
from bika.lims.api import is_string
from bika.lims.api import search
from plone.dexterity.utils import resolveDottedName
from Products.Archetypes.atapi import listTypes
from Products.CMFPlone.utils import classDoesNotImplement
from Products.CMFPlone.utils import classImplements
from senaite.core.catalog import LABEL_CATALOG
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.interfaces import ICanHaveLabels
from senaite.core.interfaces import IHaveLabels
from senaite.core.interfaces import ILabel
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

LABEL_STORAGE = "senaite.core.labels"
BEHAVIOR_ID = ICanHaveLabels.__identifier__


def get_storage(obj, default=None):
    """Get label storage for the given object

    :param obj: Content object
    :param default: default value to return
    :returns: tuple
    """
    return getattr(obj, LABEL_STORAGE, default)


def set_storage(obj, value):
    """Set the label stroage for the given object

    :param obj: The object to store the labels
    :param value: Tuple of labels
    """
    if not isinstance(value, tuple):
        raise TypeError("Expected type tuple, got %s" % type(value))
    setattr(obj, LABEL_STORAGE, value)


def query_labels(inactive=False, **kw):
    """Fetch all labels by a catalog query
    """
    catalog = SETUP_CATALOG
    query = {
        "portal_type": "Label",
        "is_active": True,
        "sort_on": "title",
    }
    # Allow to update the query with the keywords
    query.update(kw)
    if inactive:
        del query["is_active"]
    return search(query, catalog)


def get_label_by_name(name, inactive=True):
    """Fetch a label object by name

    :param name: Name of the label
    :returns: Label object or None
    """
    found = query_labels(title=name)
    if len(found) == 0:
        return None
    elif len(found) > 1:
        logger.warn("Found more than one label for '%s'"
                    "Returning the first label only" % name)
    return api.get_object(found[0])


def list_labels(inactive=False, **kw):
    """List the titles of all global labels

    :returns: List of label titles
    """
    brains = query_labels(inactive=inactive, **kw)
    labels = map(api.get_title, brains)
    return list(labels)


def create_label(label, **kw):
    """Create a new label
    """
    if not api.is_string(label):
        return None
    # Do not create duplicate labels
    existing = get_label_by_name(label, inactive=True)
    if existing:
        return existing
    # Create a new labels object
    setup = get_senaite_setup()
    return create(setup.labels, "Label", title=label, **kw)


def is_label_object(obj):
    """Checks if the given object is a label object

    :param obj: Object to check
    :returns: True if the object is a label
    """
    obj = api.get_object(obj, default=None)
    return ILabel.providedBy(obj)


def to_labels(labels):
    """Convert labels into a list of strings

    :returns: List of label strings
    """
    if not isinstance(labels, (tuple, list, set)):
        labels = tuple((labels, ))
    out = set()
    for label in labels:
        if is_label_object(label):
            out.add(api.get_title(label))
        elif label and is_string(label):
            out.add(label)
        else:
            # ignore the rest
            continue
    return tuple(out)


def catalog_object(obj):
    """Catalog the object in the label catalog
    """
    catalog = api.get_tool(LABEL_CATALOG)
    catalog.catalog_object(obj)


def uncatalog_object(obj):
    """Uncatalog the object from the label catalog
    """
    catalog = api.get_tool(LABEL_CATALOG)
    catalog.uncatalog_object(obj)


def get_obj_labels(obj):
    """Get assigned labels of the given object

    :returns: tuple of string labels
    """
    obj = get_object(obj)
    labels = get_storage(obj, default=tuple())
    return labels


def set_obj_labels(obj, labels):
    """Set the given labels to the object label storage
    """
    obj = api.get_object(obj)
    # always sort the labels before setting it to the storage
    set_storage(obj, tuple(sorted(labels)))
    # mark the object with the proper interface
    if not labels:
        noLongerProvides(obj, IHaveLabels)
        uncatalog_object(obj)
    else:
        alsoProvides(obj, IHaveLabels)
        catalog_object(obj)


def add_obj_labels(obj, labels):
    """Add one ore more labels to the object

    :param obj: the object to label
    :param labels: string or list of labels to add
    :returns: The new labels
    """
    obj = api.get_object(obj)
    # prepare the set of new labels
    new_labels = set(get_obj_labels(obj))
    for label in to_labels(labels):
        new_labels.add(label)
    # set the new labels
    set_obj_labels(obj, new_labels)
    return get_obj_labels(obj)


def del_obj_labels(obj, labels):
    """Remove labels from the object

    :param obj: the object where the labels should be removed
    :param labels: string or list of labels to remove
    :returns: The new labels
    """
    obj = api.get_object(obj)
    # prepare the set of new labels
    new_labels = set(get_obj_labels(obj))
    for label in to_labels(labels):
        new_labels.discard(label)
    # set the new labels
    set_obj_labels(obj, new_labels)
    return get_obj_labels(obj)


def search_objects_by_label(label, **kw):
    """Search for objects having one or more of the given labels

    :param label: string or list of labels to search
    :returns: Catalog results (brains)
    """
    labels = to_labels(label)
    query = {
        "labels": map(api.safe_unicode, labels),
        "sort_on": "title",
    }
    # Allow to update the query with the keywords
    query.update(kw)
    return search(query, catalog=LABEL_CATALOG)


def get_klass(portal_type):
    """Returns the implementation class of the given portal type

    :param portal_type: The portal_type to lookup the class for
    :returns: Class object
    """
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


def enable_labels_for_type(portal_type):
    """Enable labels for all objects of the given type

    :param portal_type: The portal_type to enable labeling
    """
    klass = get_klass(portal_type)
    try:
        classImplements(klass, ICanHaveLabels)
    except AttributeError:
        # '_ImmutableDeclaration' object has no attribute 'declared'
        logger.error("Type '{}' does not support labels".format(portal_type))
    # enable behavior for DX types
    if api.is_dx_type(portal_type):
        api.enable_behavior(portal_type, BEHAVIOR_ID)


def disable_labels_for_type(portal_type):
    """Disable labels for all objects of the given type

    :param portal_type: The portal_type to disable labeling
    """
    klass = get_klass(portal_type)
    try:
        classDoesNotImplement(klass, ICanHaveLabels)
    except AttributeError:
        # '_ImmutableDeclaration' object has no attribute 'declared'
        logger.error("Type '{}' does not support labels".format(portal_type))
    # disable behavior
    if api.is_dx_type(portal_type):
        api.disable_behavior(portal_type, BEHAVIOR_ID)
