from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    """LIMS-1059: Worksheet rejection workflow
    """
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow-csv')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'propertiestool')

    workflow = getToolByName(portal, 'portal_workflow')
    workflow.updateRoleMappings()

    return True
