# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import transaction
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from bika.lims import logger
from bika.lims.permissions import AddClient, EditClient
from bika.lims.permissions import ManageWorksheets


def BikaSetupModifiedEventHandler(instance, event):
    """ Event fired when BikaSetup object gets modified.
        Applies security and permission rules
    """

    if instance.portal_type != "BikaSetup":
        print("How does this happen: type is %s should be BikaSetup" % instance.portal_type)
        return

    # Security
    portal = getToolByName(instance, 'portal_url').getPortalObject()
    mp = portal.manage_permission
    if instance.getRestrictWorksheetManagement() == True \
        or instance.getRestrictWorksheetUsersAccess() == True:
        # Only LabManagers are able to create worksheets.
        mp(ManageWorksheets, ['Manager', 'LabManager'],1)
    else:
        # LabManagers, Lab Clerks and Analysts can create worksheets
        mp(ManageWorksheets, ['Manager', 'LabManager', 'LabClerk', 'Analyst'],1)


    # Allow to labclerks to add/edit clients?
    roles = ['Manager', 'LabManager']
    if instance.getAllowClerksToEditClients() == True:
        # LabClerks must be able to Add/Edit Clients
        roles += ['LabClerk']

    mp(AddClient, roles, 1)
    mp(EditClient, roles, 1)
    # Set permissions at object level
    set_client_permissions(instance, roles)


def set_client_permissions(instance, roles):
    """
    This function changes client permissions if they have changed.
    It reindexes each client object and does a transaction.commit each 100
    reindexed objects in order to flush memory and improve performance.
    :param instance: contentype object
    :param roles: A list of string as the roles to apply
    :return: None
    """
    catalog = getToolByName(instance, 'uid_catalog')
    client_chk = catalog(
        portal_type='Client',
        sort_limit=1)

    if client_chk and client_permissions_changed(client_chk[0], roles):
        clients = catalog(portal_type='Client')
        total = len(clients)
        counter = 0
        logger.info("Reindexing {} client objects...".format(total))

        for obj in clients:
            obj = obj.getObject()
            mp = obj.manage_permission
            mp(AddClient, roles, 0)
            mp(EditClient, roles, 0)
            mp(permissions.ModifyPortalContent, roles, 0)
            obj.reindexObjectSecurity()
            if counter % 100 == 0:
                logger.info(
                    'Reindexing client permissions: {0} out of {1}'
                    .format(counter, total))
                transaction.commit()
            counter += 1

        logger.info("{} Client objects reindexed".format(total))
        transaction.commit()


def client_permissions_changed(client, roles):
    """
    Checks if client permissions have been changed.
    :param client: a client zcatalog brain
    :param roles: a list of strings as role names
    :return: Boolean
    """
    has_changed = False
    if not client:
        return has_changed
    client = client.getObject()
    perms = client.rolesOfPermission(AddClient)
    labclerk = 'LabClerk'
    for perm in perms:
        if perm["name"] == labclerk:
            # will be SELECTED if the permission is granted
            if perm["selected"] == "" and labclerk in roles:
                has_changed = True
                break
            elif perm["selected"] == "SELECTED" and labclerk not in roles:
                has_changed = True
                break
    return has_changed
