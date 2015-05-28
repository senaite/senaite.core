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
    typestool = getToolByName(portal, 'portal_types')

    # update affected tools
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')

    # Add the SupplyOrderFolder /supplyorders
    try:
        typestool.constructContent(type_name="SupplyOrderFolder",
                               container=portal,
                               id='supplyorders',
                               title='Supply Orders')
        obj = portal['supplyorders']
        obj.unmarkCreationFlag()
        obj.reindexObject()
    except BadRequest:
        # folder already exists
        pass

    # /supplyorders folder permissions
    mp = portal.supplyorders.manage_permission
    mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', ], 0)
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk'], 0)
    mp('Access contents information', ['Manager', 'LabManager', 'LabClerk'], 0)
    mp(AddSupplyOrder, ['Manager', 'LabManager', 'Owner'], 0)
    portal.supplyorders.reindexObject()

    # /pricelists folder permissions
    mp = portal.pricelists.manage_permission
    mp(permissions.ListFolderContents, ['Manager', 'LabManager', 'LabClerk', ], 0)
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk'], 0)
    mp('Access contents information', ['Manager', 'LabManager', 'LabClerk'], 0)
    mp(AddPricelist, ['Manager', 'LabManager', 'LabClerk'], 0)
    portal.pricelists.reindexObject()

    return True
