# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from bika.lims.permissions import ManageWorksheets
from bika.lims.permissions import AddClient, EditClient, ManageClients

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
    clients = portal.clients.objectValues()
    if check_if_client_permissions_has_changed(clients[0], roles):
        for obj in clients:
            mp = obj.manage_permission
            mp(AddClient, roles, 0)
            mp(EditClient, roles, 0)
            mp(permissions.ModifyPortalContent, roles, 0)
            obj.reindexObject()


def check_if_client_permissions_has_changed(client, roles):
    """
    Checks if client permissions have been changed.
    :param client: a client archetype object
    :param roles: a list of strings as role names
    :return: Boolean
    """
    perms = client.rolesOfPermission(AddClient)
    labclerk = 'LabClerk'
    has_changed = False
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
