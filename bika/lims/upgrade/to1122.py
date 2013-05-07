from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from bika.lims.permissions import *


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    wf = portal.portal_workflow
    typestool = getToolByName(portal, 'portal_types')

    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')

    # Add the QueryFolder at /queries
    typestool.constructContent(type_name="QueryFolder",
                               container=portal,
                               id='queries',
                               title='Queries')
    obj = portal['queries']
    obj.unmarkCreationFlag()
    obj.reindexObject()

    # /queries folder permissions
    mp = portal.queries.manage_permission
    mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'Member', 'LabClerk', ], 0)
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Member'], 0)
    mp('Access contents information', ['Manager', 'LabManager', 'Member', 'LabClerk', 'Owner'], 0)
    mp(permissions.AddPortalContent, ['Manager', 'LabManager', 'LabClerk', 'Owner', 'Member'], 0)
    mp('ATContentTypes: Add Image', ['Manager', 'Labmanager', 'LabClerk', 'Member',], 0)
    mp('ATContentTypes: Add File', ['Manager', 'Labmanager', 'LabClerk', 'Member',], 0)
    portal.queries.reindexObject()

    return True
