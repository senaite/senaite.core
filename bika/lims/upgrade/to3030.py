from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest


def upgrade(tool):
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    workflow = getToolByName(portal, "portal_workflow")

    # /arimports folder permissions
    mp = portal.arimports.manage_permission
    mp(ManageARImport, ['Manager', ], 1)
    mp(permissions.ListFolderContents, ['Manager','Member',], 1)
    mp(permissions.AddPortalContent, ['Manager', ], 0)
    mp(permissions.DeleteObjects, ['Manager'], 0)
    mp(permissions.View, ['Manager','Member'], 0)
    portal.arimports.reindexObject()
    try:
        workflow.doActionFor(portal.arimports, "hide")
    except:
        pass
    portal.arimports.setLayout('@@arimports')
    return True
