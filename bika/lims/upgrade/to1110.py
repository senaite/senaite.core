import logging

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.CMFCore import permissions
from bika.lims.permissions import *

from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.Permissions import ApplyVersionControl
from Products.CMFEditions.Permissions import SaveNewVersion
from Products.CMFEditions.Permissions import AccessPreviousVersions


def upgrade(tool):
    """
    Add RegulatoryInspectors group and RegulatoryInspector role.
    Fix permissions: LabClerks don't see analysis results
    """

    portal = aq_parent(aq_inner(tool))

    portal.acl_users.portal_role_manager.addRole('RegulatoryInspector')
    portal._addRole('RegulatoryInspector')
    portal_groups = portal.portal_groups
    portal_groups.addGroup('RegulatoryInspectors',
                           title = "Regulatory Inspectors",
                           roles = ['Member', 'RegulatoryInspector', ])

    # setup permissions
    mp = portal.manage_permission
    mp(ApplyVersionControl, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'RegulatoryInspector'], 1)
    mp(SaveNewVersion, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'RegulatoryInspector'], 1)
    mp(AccessPreviousVersions, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Owner', 'RegulatoryInspector'], 1)
    mp(ManageAnalysisRequests, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner', 'RegulatoryInspector'], 1)
    mp(ManageSamples, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner', 'RegulatoryInspector'], 1)
    mp(ManageWorksheets, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'RegulatoryInspector'], 1)
    mp(EditWorksheet, ['Manager', 'LabManager', 'Analyst'], 1)
    mp(ViewResults, ['Manager', 'LabManager', 'Analyst', 'Sampler','RegulatoryInspector'], 1)
    portal.bika_setup.reindexObject()

    # /worksheets folder permissions
    mp = portal.worksheets.manage_permission
    mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'RegulatoryInspector'], 0)
    mp(permissions.View, ['Manager', 'LabManager', 'Analyst', 'RegulatoryInspector'], 0)
    mp('Access contents information', ['Manager', 'LabManager', 'Analyst', 'RegulatoryInspector'], 0)
    portal.worksheets.reindexObject()

    # /batches folder permissions
    mp = portal.batches.manage_permission
    mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Authenticated', 'RegulatoryInspector'], 0)
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'RegulatoryInspector'], 0)
    mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Authenticated', 'RegulatoryInspector'], 0)
    portal.batches.reindexObject()

    # /analysisrequests folder permissions
    mp = portal.analysisrequests.manage_permission
    mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'RegulatoryInspector'], 0)
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'RegulatoryInspector'], 0)
    mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'RegulatoryInspector'], 0)
    portal.analysisrequests.reindexObject()

    # /samples folder permissions
    mp = portal.samples.manage_permission
    mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'RegulatoryInspector'], 0)
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'RegulatoryInspector'], 0)
    mp('Access contents information', ['Manager', 'LabManager', 'LabClerk', 'Analyst','Sampler', 'Preserver', 'RegulatoryInspector'], 0)
    portal.samples.reindexObject()

    return True
