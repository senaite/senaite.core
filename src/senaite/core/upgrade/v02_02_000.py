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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.interfaces.analysis import IRequestAnalysis
from collections import defaultdict
from senaite.core import logger
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.catalog import WORKSHEET_CATALOG
from senaite.core.config import PROJECTNAME as product
from senaite.core.interfaces import IContentMigrator
from senaite.core.setuphandlers import _run_import_step
from senaite.core.setuphandlers import add_dexterity_setup_items
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import copy_snapshots
from senaite.core.upgrade.utils import delete_object
from senaite.core.upgrade.utils import uncatalog_object
from senaite.core.upgrade.utils import UpgradeUtils
from zope.component import getMultiAdapter

version = "2.2.0"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # -------- ADD YOUR STUFF BELOW --------

    # run import steps located in bika.lims profiles
    _run_import_step(portal, "rolemap", profile="profile-bika.lims:default")

    # run import steps located in senaite.core profiles
    setup.runImportStepFromProfile(profile, "viewlets")
    setup.runImportStepFromProfile(profile, "rolemap")
    setup.runImportStepFromProfile(profile, "workflow")
    setup.runImportStepFromProfile(profile, "typeinfo")

    # Setup the permission for the edition of analysis conditions
    setup_edit_analysis_conditions(portal)

    # Preserve all information from service conditions in Sample
    update_analysis_conditions(portal)

    # Add sample containers folder
    add_dexterity_setup_items(portal)

    # Migrate containes
    migrate_containers_to_dx(portal)

    # Migrate worksheet layouts
    migrate_worksheet_layouts(portal)

    # Remove explicit owner role for contacts
    remove_contacts_ownership(portal)

    # Fix analyses conditions
    fix_analyses_conditions(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def migrate_containers_to_dx(portal):
    """Converts existing containers to Dexterity
    """
    logger.info("Convert Containers to Dexterity ...")

    old_id = "bika_containers"
    new_id = "sample_containers"

    setup = api.get_setup()
    old = setup.get(old_id)
    new = setup.get(new_id)

    # return if the old container is already gone
    if not old:
        return

    # uncatalog the old object
    uncatalog_object(old)

    # Mapping from schema field name to a tuple of
    # (accessor, target field name, default value)
    schema_mapping = {
        "title": ("Title", "title", ""),
        "description": ("Description", "description", ""),
        "ContainerType": ("getContainerType", "containertype", None),
        "Capacity": ("getCapacity", "capacity", "0 ml"),
        "PrePreserved": ("getPrePreserved", "prepreserved", False),
        "Preservation": ("getPreservation", "preservation", None),
        "SecuritySealIntact": ("getSecuritySealIntact", "security_seal_intact", False),
    }

    # copy items from old -> new container
    for src in old.objectValues():
        target = api.create(new, "SampleContainer")
        migrator = getMultiAdapter(
            (src, target), interface=IContentMigrator)
        migrator.migrate(schema_mapping, delete_src=False)

    # copy snapshots for the container
    copy_snapshots(old, new)

    # delete the old object
    delete_object(old)

    logger.info("Convert Containers to Dexterity [DONE]")


def setup_edit_analysis_conditions(portal):
    """Updates role mappings for analyses that are not yet verified for the
    permission "Edit Analysis Conditions" to become effective
    """
    logger.info("Updating role mappings for Analyses ...")
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById("senaite_analysis_workflow")
    query = {
        "portal_type": "Analysis",
        "review_state": ["registered", "unassigned", "assigned"]
    }
    brains = api.search(query, ANALYSIS_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Updating role mappings: {0}/{1}".format(num, total))
        obj = api.get_object(brain)
        workflow.updateRoleMappingsFor(obj)
        obj.reindexObject(idxs=["allowedRolesAndUsers"])

    logger.info("Updating role mappings for Analyses [DONE]")


def update_analysis_conditions(portal):
    """Walks through all analyses awaiting for result and sets all information
    from Service Conditions to them
    """
    logger.info("Updating service conditions for Analyses ...")
    query = {
        "portal_type": "Analysis",
        "review_state": ["registered", "unassigned", "assigned", "to_be_verified"]
    }
    brains = api.search(query, ANALYSIS_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Updating conditions: {0}/{1}".format(num, total))

        analysis = api.get_object(brain)
        if not IRequestAnalysis.providedBy(analysis):
            continue

        # Extract the original conditions set at service level
        service = analysis.getAnalysisService()
        service_conditions = service.getConditions()
        service_conditions = dict(map(lambda cond: (cond.get("title"), cond),
                                      service_conditions))

        # Extract the conditions from the analysis and update them accordingly
        conditions = analysis.getConditions()
        for condition in conditions:
            title = condition.get("title")
            orig_condition = service_conditions.get(title, {})
            condition.update({
                "required": orig_condition.get("required", ""),
                "choices": orig_condition.get("choices", ""),
                "description": orig_condition.get("description", ""),
            })

        # Reset the conditions
        analysis.setConditions(conditions)

    logger.info("Updating service conditions for Analyses [DONE]")


def migrate_worksheet_layouts(portal):
    """Walks through all worksheets and migrates the layout settings like this:

       1 -> analyses_classic_view
       2 -> analyses_transposed_view
    """
    logger.info("Migrating worksheet layouts ...")
    mapping = {"1": "analyses_classic_view", "2": "analyses_transposed_view"}
    query = {"portal_type": "Worksheet"}
    brains = api.search(query, WORKSHEET_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Migrating worksheet: {0}/{1}".format(num, total))

        obj = api.get_object(brain)
        layout = mapping.get(str(obj.getResultsLayout()), None)
        if layout:
            # set the new layout
            obj.setResultsLayout(layout)
    
    logger.info("Update default worksheet layout for BikaSetup ...")

    setup = api.get_setup()
    default_layout = mapping.get(str(setup.getWorksheetLayout()), None)
    if default_layout:
        setup.setWorksheetLayout(default_layout)

    logger.info("Migrating worksheet layouts [DONE]")


def remove_contacts_ownership(portal):
    logger.info("Removing Contacts explicit ownership ...")

    def remove_owner_role(obj, usernames):
        reindex = False
        obj_roles = obj.get_local_roles()
        for user, roles in obj_roles:
            if user not in usernames:
                continue
            if "Owner" not in roles:
                continue

            # Need to update the local roles for this object
            local_roles = filter(lambda r: r != "Owner", roles)
            if local_roles:
                obj.manage_setLocalRoles(user, local_roles)
            else:
                obj.manage_delLocalRoles([user])
            reindex = True

        # Iterate through children for ownership removal
        for child in obj.objectValues():
            remove_owner_role(child, usernames)

        # Only reindex if local roles have changed
        if reindex:
            obj.reindexObjectSecurity()

    # Extract contacts and group them by client
    client_contacts = defaultdict(list)
    query = {"portal_type": "Contact"}
    for brain in api.search(query):
        contact = api.get_object(brain)
        username = contact.getUsername()
        if not username:
            continue

        client = api.get_parent(contact)
        client_uid = api.get_uid(client)
        client_contacts[client_uid].append(username)

    # Remove the owner role for all contacts at once for each client
    client_uids = client_contacts.keys()
    total = len(client_uids)
    for num, client_uid in enumerate(client_uids):
        logger.info("Removing 'Owner' roles: {0}/{1}".format(num+1, total))
        usernames = client_contacts.get(client_uid)
        client = api.get_object(client_uid)
        remove_owner_role(client, usernames)

    logger.info("Removing Contacts explicit ownership [DONE]")


def fix_analyses_conditions(portal):
    """Fixes the analyses conditions
    """
    def to_condition(condition):
        # UID, type and title are required
        uid = condition.get("uid")
        title = condition.get("title")
        cond_type = condition.get("type")
        if not all([api.is_uid(uid), title, cond_type]):
            return None

        condition_info = {
            "uid": uid,
            "title": title,
            "type": cond_type,
            "description": "",
            "choices": "",
            "default": "",
            "required": "",
            "value": "",
        }
        condition = dict(condition)
        condition_info.update(condition)
        return condition_info

    logger.info("Reassign analyses conditions ...")
    query = {
        "portal_type": "Analysis",
        "review_state": ["registered", "unassigned", "assigned",
                         "to_be_verified"]
    }
    brains = api.search(query, ANALYSIS_CATALOG)
    for brain in brains:
        analysis = api.get_object(brain)
        if not IRequestAnalysis.providedBy(analysis):
            continue

        sample = analysis.getRequest()
        conditions = sample.getServiceConditions()
        if not conditions:
            continue

        # Sanitize and reassign the conditions
        conditions = filter(None, map(to_condition, conditions))
        sample.setServiceConditions(conditions)

    logger.info("Reassign analyses conditions [DONE]")
