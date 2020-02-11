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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.permissions import ListFolderContents
from Products.CMFCore.permissions import View
from bika.lims.api import security
from bika.lims.interfaces import IInternalUse
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
from zope.lifecycleevent import modified


def ObjectModifiedEventHandler(instance, event):
    """Actions to be taken when AnalysisRequest object is modified
    """
    # If Internal Use value has been modified, apply suitable permissions
    internal_use = instance.getInternalUse()
    if internal_use != IInternalUse.providedBy(instance):

        # Update permissions for current sample
        update_internal_use_permissions(instance)

        # Mark/Unmark all analyses with IInternalUse to control their
        # visibility in results reports
        for analysis in instance.objectValues("Analysis"):
            analysis.setInternalUse(internal_use)
            analysis.reindexObjectSecurity()

        # If internal use is True, cascade same setting to partitions
        if internal_use:
            for partition in instance.getDescendants():
                partition.setInternalUse(internal_use)
                # Notify the partition has been modified
                modified(partition)


def AfterTransitionEventHandler(instance, event):
    """Actions to be taken when AnalsysiRequest object has been transitioned.
    This function does not superseds workflow.analysisrequest.events, rather it
    only updates the permissions in accordance with InternalUse value
    """
    # Permissions for a given object change after transitions to meet with the
    # workflow definition. InternalUse prevents Clients to access to Samples
    # and analyses as well. Therefore, we have to update the permissions
    # manually here to override those set by default
    update_internal_use_permissions(instance)


def update_internal_use_permissions(analysis_request):
    """Updates the permissions for the AnalysisRequest object passed in
    accordance with the value set for field InternalUse
    """
    if analysis_request.getInternalUse():
        # Revoke basic permissions from Owner (the client contact)
        revoke_permission(View, "Owner", analysis_request)
        revoke_permission(ListFolderContents, "Owner", analysis_request)
        revoke_permission(AccessContentsInformation, "Owner", analysis_request)

        # Mark the Sample for Internal use only
        alsoProvides(analysis_request, IInternalUse)

    else:
        # Restore basic permissions (acquired=1)
        analysis_request.manage_permission(View, [], acquire=1)
        analysis_request.manage_permission(ListFolderContents, [], acquire=1)
        analysis_request.manage_permission(AccessContentsInformation, [],
                                           acquire=1)

        # Unmark the Sample
        noLongerProvides(analysis_request, IInternalUse)

    analysis_request.reindexObjectSecurity()
    analysis_request.reindexObject(idxs="getInternalUse")


def gather_roles_for_permission(permission, obj):
    """Extract all the effective roles for a given permission and object,
    acquired roles included
    """
    roles = security.get_roles_for_permission(permission, obj)
    if obj.acquiredRolesAreUsedBy(permission):
        roles.extend(gather_roles_for_permission(permission, obj.aq_parent))
    return list(set(roles))


def revoke_permission(permission, role, obj):
    """Revokes a permission for a given role and object
    """
    roles = gather_roles_for_permission(permission, obj)
    if role in roles:
        roles.remove(role)
    obj.manage_permission(permission, roles)
