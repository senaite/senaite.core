from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    workflow = getToolByName(portal, "portal_workflow")

    # /arimports folder permissions
    mp = portal.arimports.manage_permission
    mp(ManageARImport, ['Manager', 'LabManager', 'Owner'], 1)
    mp(permissions.ListFolderContents, ['Member'], 1)
    mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'Owner'], 0)
    mp(permissions.DeleteObjects, ['Manager', 'LabManager', 'Owner'], 0)
    mp(permissions.View, ['Manager', 'LabManager'], 0)
    portal.arimports.reindexObject()
    try:
        workflow.doActionFor(portal.arimports, "hide")
    except:
        pass
    portal.arimports.setLayout('@@arimports')
    return True
