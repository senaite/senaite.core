# -*- coding: utf-8 -*-
#
# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from bika.lims import api
from bika.lims import logger

"""Catalog Dexterity Objects that appear in more than one catalog
"""


def reindexMovedObject(obj, event):
    """Reindex moved/renamed object
    """

    bika_catalogs = getattr(obj, "_bika_catalogs", [])

    for name in bika_catalogs:
        logger.debug("Reidexing moved object '{}' in catalog '{}'".format(
            obj.getId(), name))
        catalog = api.get_tool(name)

        # old and new name
        old_name = event.oldName
        new_name = event.newName

        if old_name and new_name:
            old_parent = event.oldParent
            old_ppath = api.get_path(old_parent)
            old_path = "/".join([old_ppath, old_name])

            # uncatalog the old path
            catalog.uncatalog_object(old_path)

            # reindex object
            catalog.reindexObject(obj)


def indexObject(obj, event):
    """Additionally index the object into the bika catalogs
    """

    bika_catalogs = getattr(obj, "_bika_catalogs", [])
    for name in bika_catalogs:
        logger.debug("Indexing object '{}' into catalog '{}'".format(
            obj.getId(), name))
        catalog = api.get_tool(name)
        catalog.indexObject(obj)


def unindexObject(obj, event):
    """Remove an object from all registered catalogs
    """

    bika_catalogs = getattr(obj, "_bika_catalogs", [])
    for name in bika_catalogs:
        logger.debug("Unindexing object '{}' from catalog '{}'".format(
            obj.getId(), name))
        catalog = api.get_tool(name)
        catalog.unindexObject(obj)


def reindexObject(obj, event):
    """Reindex an object in all registered catalogs
    """

    bika_catalogs = getattr(obj, "_bika_catalogs", [])
    for name in bika_catalogs:
        logger.debug("Unindexing object '{}' from catalog '{}'".format(
            obj.getId(), name))
        catalog = api.get_tool(name)
        catalog.reindexObject(obj)


def reindexObjectSecurity(obj, event):
    """Reindex only security information on catalogs
    """

    bika_catalogs = getattr(obj, "_bika_catalogs", [])
    for name in bika_catalogs:
        logger.debug("Reindex security for object '{}' from catalog '{}'".format(
            obj.getId(), name))
        catalog = api.get_tool(name)
        catalog.reindexObject(obj,
                              idxs=obj._cmf_security_indexes,
                              update_metadata=0)
