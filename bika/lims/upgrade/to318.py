from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.Archetypes.BaseContent import BaseContent
from bika.lims.upgrade import stub
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    """Upgrade step required for Bika LIMS 3.1.8
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # Reread typeinfo to update/add the modified/added types
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    # Updated profile steps
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow_csv')
    # Update workflow permissions
    wf = getToolByName(portal, 'portal_workflow')
    wf.updateRoleMappings()


    # Migrations
    return True
