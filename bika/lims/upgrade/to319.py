from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import AddMultifile
from Products.Archetypes.BaseContent import BaseContent
from bika.lims.upgrade import stub
from bika.lims import logger

def upgrade(tool):
    """Upgrade step required for Bika LIMS 3.1.9
    """
    portal = aq_parent(aq_inner(tool))
    # Adding new feature multiple profiles per Analysis Request
    multipleAnalysisProfiles(portal)
    setup = portal.portal_setup
    # Updated profile steps
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow-csv')
    # important info about upgrade steps in
    # http://stackoverflow.com/questions/7821498/is-there-a-good-reference-list-for-the-names-of-the-genericsetup-import-steps
    setup.runImportStepFromProfile('profile-bika.lims:default', 'skins')
    # Update workflow permissions
    wf = getToolByName(portal, 'portal_workflow')
    wf.updateRoleMappings()

    qi = portal.portal_quickinstaller
    ufrom = qi.upgradeInfo('bika.lims')['installedVersion']
    logger.info("Upgrading Bika LIMS: %s -> %s" % (ufrom, '319'))

    # Migrations

    return True

def multipleAnalysisProfiles(portal):
    """
    All the logic used to use multiple analysis profile selection in analysis request.
    We have to add some indexes and columns in setuphandler.py and also we have to move all analysis profiles from the
    analysis request's content field "profile" to profiles
    """
    bc = getToolByName(portal, 'bika_catalog', None)
    if 'getProfilesTitle' not in bc.indexes():
        bc.addIndex('getProfilesTitle', 'FieldIndex')
        bc.addColumn('getProfilesTitle')
    # Moving from profile to profiles
    ars = bc(portal_type="AnalysisRequest")
    for ar_brain in ars:
        ar = ar_brain.getObject()
        if not ar.getProfiles():
            ar.setProfiles(ar.getProfile())
