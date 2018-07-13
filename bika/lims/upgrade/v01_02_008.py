# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import logger
from bika.lims import api
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from Products.CMFCore import permissions

version = '1.2.8'  # Remember version number in metadata.xml and setup.py
profile = 'profile-{0}:default'.format(product)


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)
    setup = portal.portal_setup

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # -------- ADD YOUR STUFF HERE --------

    # Revert upgrade actions performed due to #893 (reverted)
    revert_client_permissions_for_batches(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def revert_client_permissions_for_batches(portal):
    # Disallow client contacts to see the list of batches
    del_permission_for_role(portal.batches, permissions.View, 'Client')

    # Remove permission View for role Client in workflow bika_batch_workflow
    # and review state is 'open'
    remopen = del_permissions_for_role_in_workflow('bika_batch_workflow',
                                                   'open', ['Client'],
                                                   [permissions.View])

    # Remove permission View for role Client in workflow bika_batch_workflow
    # and review state is 'open'
    remclos = del_permissions_for_role_in_workflow('bika_batch_workflow',
                                                   'closed', ['Client'],
                                                   [permissions.View])
    if remopen or remclos:
        # Update rolemappings for batches, but only if necessary
        wtool = api.get_tool("portal_workflow")
        workflow = wtool.getWorkflowById('bika_batch_workflow')
        catalog = api.get_tool('bika_catalog')
        brains = catalog(portal_type='Batch')
        counter = 0
        total = len(brains)
        logger.info(
            "Changing permissions for Batch objects: {0}".format(total))
        for brain in brains:
            obj = api.get_object(brain)
            workflow.updateRoleMappingsFor(obj)
            obj.reindexObject()
            counter += 1
            if counter % 100 == 0:
                logger.info(
                    "Changing permissions for Batch objects: " +
                    "{0}/{1}".format(counter, total))
        logger.info(
            "Changed permissions for Batch objects: " +
            "{0}/{1}".format(counter, total))


def del_permission_for_role(folder, permission, role):
    """Removes a permission from the given role and given folder
    :param folder: folder from which the permission for the role has to be removed
    :param permission: the permission to be removed
    :param role: role from which the permission must be removed
    :return True if succeed, otherwise, False
    """
    roles = filter(lambda perm: perm.get('selected') == 'SELECTED',
                   folder.rolesOfPermission(permission))
    roles = map(lambda perm_role: perm_role['name'], roles)
    if role not in roles:
        # Nothing to do, the role has not the permission
        logger.info(
            "Role '{}' has not the permission {} assigned for {}"
                .format(role, repr(permission), repr(folder)))
        return False
    roles.remove(role)
    acquire = folder.acquiredRolesAreUsedBy(
        permission) == 'CHECKED' and 1 or 0
    folder.manage_permission(permission, roles=roles, acquire=acquire)
    folder.reindexObject()
    logger.info(
        "Removed permission {} from role '{}' for {}"
            .format(repr(permission), role, repr(folder)))
    return True


def del_permissions_for_role_in_workflow(wfid, wfstate, roles, permissions):
    """Removes the permissions passed in for the given roles and for the
    specified workflow and its state
    :param wfid: workflow id
    :param wfstate: workflow state
    :param roles: roles the permissions must be removed from
    :param permissions: permissions to be removed
    :return True if succeed, otherwise, False
    """
    wtool = api.get_tool("portal_workflow")
    workflow = wtool.getWorkflowById(wfid)
    if not workflow:
        return False
    state = workflow.states.get(wfstate, None)
    if not state:
        return False
    # Get the permission-roles that apply to this state
    removed = False
    for permission in permissions:
        # Get the roles that apply for this permission
        permission_info = state.getPermissionInfo(permission)
        acquired = permission_info['acquired']
        st_roles = permission_info['roles']
        ef_roles = filter(lambda role: role not in roles, st_roles)
        if len(ef_roles) == len(st_roles):
            continue

        logger.info("Removing roles {} from permission {} in {} with state {}"
                    .format(repr(roles), repr(permission), wfid, wfstate))
        state.setPermission(permission, acquired, ef_roles)
        removed = True
    return removed
