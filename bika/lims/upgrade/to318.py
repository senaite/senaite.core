from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import AddMultifile
from Products.Archetypes.BaseContent import BaseContent
from bika.lims.upgrade import stub


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

    # Adding Multifile content type
    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('Multifile', ['bika_setup_catalog', ])
    # Update workflow permissions
    wf = getToolByName(portal, 'portal_workflow')
    wf.updateRoleMappings()
    # Define permissions for Multifile
    mp = portal.manage_permission
    mp(AddMultifile, ['Manager', 'Owner', 'LabManager', 'LabClerk'], 1)


    # Migrations
    return True
