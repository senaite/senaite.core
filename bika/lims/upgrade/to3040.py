from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    """LIMS-1059: Worksheet rejection workflow
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow-csv')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'propertiestool')

    workflow = getToolByName(portal, 'portal_workflow')
    workflow.updateRoleMappings()

    return True
