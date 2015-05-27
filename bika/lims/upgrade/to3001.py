from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    mp = portal.bika_setup.manage_permission
    mp('Access contents information', ['Authenticated', 'Analyst'], 1)
    mp(permissions.View, ['Authenticated', 'Analyst'], 1)
    portal.bika_setup.reindexObject()

    for obj in portal.bika_setup.bika_analysisservices.objectValues():
        mp = obj.manage_permission
        mp(permissions.View, ['Manager', 'LabManager', 'Analyst'], 0)
        mp('Access contents information', ['Manager', 'LabManager', 'Member', 'LabClerk', 'Analyst', 'Sampler', 'Preserver', 'Owner'], 0)
        obj.reindexObject()

    wf = getToolByName(portal, 'portal_workflow')
    # update affected tools
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow-csv')
    wf.updateRoleMappings()

    return True
