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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.CMFCore import permissions as cmf_permissions
from bika.lims.api import security
from bika.lims.interfaces import IInternalUse
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


def ObjectModifiedEventHandler(instance, event):
    """Actions to be taken when AnalysisRequest object is modified
    """
    # If Internal Use value has been modified, apply suitable permissions
    internal_use = instance.getInternalUse()
    if internal_use != IInternalUse.providedBy(instance):
        # Update permissions for current sample
        update_internal_use_permissions(instance)


def AfterTransitionEventHandler(instance, event):
    """Actions to be taken when AnalsysiRequest object has been transitioned.
    This function does not superseds workflow.analysisrequest.events, rather it
    only updates the permissions in accordance with InternalUse value
    """
    update_internal_use_permissions(instance)


def update_internal_use_permissions(analysis_request):
    """Updates the permissions for the AnalysisRequest object passed in
    accordance with the value set for field InternalUse
    """
    internal_use = analysis_request.getInternalUse()

    # View and List Folder Content permissions
    view = cmf_permissions.View
    lfc = cmf_permissions.ListFolderContents
    if internal_use:
        # Note Owner (even if is a client contact) will always be able to
        # access this Sample!
        security.revoke_permission_for(analysis_request, view, "Client")
        security.revoke_permission_for(analysis_request, lfc, "Client")
        alsoProvides(analysis_request, IInternalUse)
    else:
        security.grant_permission_for(analysis_request, view, "Client")
        security.grant_permission_for(analysis_request, lfc, "Client")
        noLongerProvides(analysis_request, IInternalUse)

    analysis_request.reindexObject()
