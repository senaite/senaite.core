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
# Copyright 2018-2023 by it's authors.
# Some rights reserved, see README and LICENSE.

import transaction
from Acquisition import aq_base
from bika.lims import api
from senaite.core import logger
from senaite.core.api.catalog import add_index
from senaite.core.api.catalog import del_column
from senaite.core.api.catalog import del_index
from senaite.core.api.catalog import reindex_index
from senaite.core.catalog import CLIENT_CATALOG
from senaite.core.catalog import REPORT_CATALOG
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.config import PROJECTNAME as product
from senaite.core.setuphandlers import add_dexterity_items
from senaite.core.setuphandlers import setup_catalog_mappings
from senaite.core.setuphandlers import setup_core_catalogs
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.core.upgrade.utils import uncatalog_brain
from senaite.core.permissions import ManageBika

version = "2.5.0"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)

CONTENT_ACTIONS = [
    # portal_type, action
    ("Client", {
        "id": "manage_access",
        "name": "Manage Access",
        "action": "string:${object_url}/@@sharing",
        # NOTE: We use this permission to hide the action from logged in client
        # contacts
        "permission": ManageBika,
        # "permission": "Sharing page: Delegate roles",
        "category": "object",
        "visible": True,
        "icon_expr": "",
        "link_target": "",
        "condition": "",
        "insert_after": "edit",
    }),
]


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # -------- ADD YOUR STUFF BELOW --------

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def rebuild_sample_zctext_index_and_lexicon(tool):
    """Recreate sample listing_searchable_text ZCText index and Lexicon
    """
    # remove the existing index
    index = "listing_searchable_text"
    del_index(SAMPLE_CATALOG, index)
    # remove the Lexicon
    catalog = api.get_tool(SAMPLE_CATALOG)
    if "Lexicon" in catalog.objectIds():
        catalog.manage_delObjects("Lexicon")
    # recreate the index + lexicon
    add_index(SAMPLE_CATALOG, index, "ZCTextIndex")
    # reindex
    reindex_index(SAMPLE_CATALOG, index)


@upgradestep(product, version)
def setup_labels(tool):
    """Setup labels for SENAITE
    """
    logger.info("Setup Labels")
    portal = api.get_portal()

    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")
    tool.runImportStepFromProfile(profile, "plone.app.registry")
    setup_core_catalogs(portal)

    items = [
        ("labels",
         "Labels",
         "Labels")
    ]
    setup = api.get_senaite_setup()
    add_dexterity_items(setup, items)


def setup_client_catalog(tool):
    """Setup client catalog
    """
    logger.info("Setup Client Catalog ...")
    portal = api.get_portal()

    # setup and rebuild client_catalog
    setup_catalog_mappings(portal)
    setup_core_catalogs(portal)
    client_catalog = api.get_tool(CLIENT_CATALOG)
    client_catalog.clearFindAndRebuild()

    # portal_catalog cleanup
    uncatalog_type("Client", catalog="portal_catalog")

    logger.info("Setup Client Catalog [DONE]")


def uncatalog_type(portal_type, catalog="portal_catalog", **kw):
    """Uncatalog all entries of the given type from the catalog
    """
    query = {"portal_type": portal_type}
    query.update(kw)
    brains = api.search(query, catalog=catalog)
    for brain in brains:
        uncatalog_brain(brain)


def setup_catalogs(tool):
    """Setup all core catalogs and ensure all indexes are present
    """
    logger.info("Setup Catalogs ...")
    portal = api.get_portal()

    setup_catalog_mappings(portal)
    setup_core_catalogs(portal)

    logger.info("Setup Catalogs [DONE]")


def update_report_catalog(tool):
    """Update indexes in report catalog and add new metadata columns
    """
    logger.info("Update report catalog ...")
    portal = api.get_portal()

    # ensure new indexes are created
    setup_catalog_mappings(portal)
    setup_core_catalogs(portal)

    # remove columns
    del_column(REPORT_CATALOG, "getClientTitlegetClientURL")
    del_column(REPORT_CATALOG, "getDatePrinted")

    logger.info("Update report catalog [DONE]")


def create_client_groups(tool):
    """Create for all Clients an explicit Group
    """
    logger.info("Create client groups ...")
    clients = api.search({"portal_type": "Client"}, CLIENT_CATALOG)
    total = len(clients)
    for num, client in enumerate(clients):
        obj = api.get_object(client)
        logger.info("Processing client %s/%s: %s"
                    % (num+1, total, obj.getName()))

        # recreate the group
        obj.remove_group()

        group = obj.create_group()
        # add all linked client contacts to the group
        for contact in obj.getContacts():
            user = contact.getUser()
            if not user:
                continue
            logger.info("Adding user '%s' to the client group '%s'"
                        % (user.getId(), group.getId()))
            obj.add_user_to_group(user)

    logger.info("Create client groups [DONE]")


def reindex_client_security(tool):
    """Reindex client object security to grant the owner role for the client
       group to all contents
    """
    logger.info("Reindex client security ...")

    clients = api.search({"portal_type": "Client"}, CLIENT_CATALOG)
    total = len(clients)
    for num, client in enumerate(clients):
        obj = api.get_object(client)
        logger.info("Processing client %s/%s: %s"
                    % (num+1, total, obj.getName()))
        _recursive_reindex_object_security(obj)

        if num and num % 1000 == 0:
            # reduce memory size of the transaction
            transaction.savepoint()

        # Flush the object from memory
        obj._p_deactivate()

    logger.info("Reindex client security [DONE]")


def _recursive_reindex_object_security(obj):
    """Recursively reindex object security for the given object
    """
    if hasattr(aq_base(obj), "objectValues"):
        for child_obj in obj.objectValues():
            _recursive_reindex_object_security(child_obj)
    obj.reindexObject(idxs=["allowedRolesAndUsers"])


def add_content_actions(tool):
    logger.info("Add cotent actions ...")
    portal_types = api.get_tool("portal_types")
    for record in CONTENT_ACTIONS:
        portal_type, action = record
        type_info = portal_types.getTypeInfo(portal_type)
        action_id = action.get("id")
        # remove any previous added actions with the same ID
        _remove_action(type_info, action_id)
        # pop out the position info
        insert_after = action.pop("insert_after", None)
        # add the action
        type_info.addAction(**action)
        # sort the action to the right position
        actions = type_info._cloneActions()
        action_ids = map(lambda a: a.id, actions)
        if insert_after in action_ids:
            ref_index = action_ids.index(insert_after)
            index = action_ids.index(action_id)
            action = actions.pop(index)
            actions.insert(ref_index + 1, action)
            type_info._actions = tuple(actions)

        logger.info("Added action id '%s' to '%s'",
                    action_id, portal_type)
    logger.info("Add content actions [DONE]")


def _remove_action(type_info, action_id):
    """Removes the action id from the type passed in
    """
    actions = map(lambda action: action.id, type_info._actions)
    if action_id not in actions:
        return True
    index = actions.index(action_id)
    type_info.deleteActions([index])
    return _remove_action(type_info, action_id)
