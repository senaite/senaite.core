# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import ManageSupplyOrders, ManageLoginDetails
from bika.lims.interfaces import IAnalysisRequest


def ObjectModifiedEventHandler(obj, event):
    """ Various types need automation on edit.
    """
    if not hasattr(obj, 'portal_type'):
        return

    if obj.portal_type == 'Calculation':
        pr = getToolByName(obj, 'portal_repository')
        uc = getToolByName(obj, 'uid_catalog')
        obj = uc(UID=obj.UID())[0].getObject()
        version_id = obj.version_id if hasattr(obj, 'version_id') else 0

        backrefs = obj.getBackReferences('MethodCalculation')
        for i, target in enumerate(backrefs):
            target = uc(UID=target.UID())[0].getObject()
            pr.save(obj=target, comment="Calculation updated to version %s" %
                (version_id + 1,))
            reference_versions = getattr(target, 'reference_versions', {})
            reference_versions[obj.UID()] = version_id + 1
            target.reference_versions = reference_versions

    elif obj.portal_type == 'Client':
        mp = obj.manage_permission
        mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner'], 0)
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk',  'Analyst', 'Sampler', 'Preserver', 'Owner'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
        mp(ManageSupplyOrders, ['Manager', 'LabManager', 'Owner', 'LabClerk'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'Member', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner'], 0)

    elif obj.portal_type == 'Contact':
        # Contacts need to be given "Owner" local-role on their Client.
        mp = obj.manage_permission
        mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Owner', 'Analyst', 'Sampler', 'Preserver'], 0)
        mp(permissions.ModifyPortalContent, ['Manager', 'LabManager', 'Owner', 'LabClerk'], 0)
        mp(ManageLoginDetails, ['Manager', 'LabManager', 'LabClerk'], 0)
        # Verify that the Contact details are the same as the Plone user.
        contact_username = obj.Schema()['Username'].get(obj)
        if contact_username:
            contact_email = obj.Schema()['EmailAddress'].get(obj)
            contact_fullname = obj.Schema()['Fullname'].get(obj)
            mt = getToolByName(obj, 'portal_membership')
            member = mt.getMemberById(contact_username)
            if member:
                properties = {'username': contact_username,
                              'email': contact_email,
                              'fullname': contact_fullname}
                member.setMemberProperties(properties)

    elif obj.portal_type == 'AnalysisCategory':
        # If the analysis category's Title is modified, we must
        # re-index all services and analyses that refer to this title.
        for i in [['Analysis', 'bika_analysis_catalog'],
                  ['AnalysisService', 'bika_setup_catalog']]:
            cat = getToolByName(obj, i[1])
            brains = cat(portal_type=i[0], getCategoryUID=obj.UID())
            for brain in brains:
                brain.getObject().reindexObject(idxs=['getCategoryTitle'])
