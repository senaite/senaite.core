from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = '1.1.3'
profile = 'profile-{0}:default'.format(product)


@upgradestep(product, version)
def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        # The currently installed version is more recent than the target
        # version of this upgradestep
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # Updating profile steps:
    # list of the generic setup import step names:
    # --> portal.portal_setup.getSortedImportSteps() <---
    #
    # if you want more metadata use this:
    # --> portal.portal_setup.getImportStepMetadata('jsregistry') <---
    #
    # important info about upgrade steps in
    # http://stackoverflow.com/questions/7821498/is-there-a-good-reference-list-for-the-names-of-the-genericsetup-import-steps

    # New ARImports workflow
    setup.runImportStepFromProfile(profile, 'workflow')

    # Attachments must be present in a catalog, otherwise the idserver
    # will fall apart.  https://github.com/senaite/bika.lims/issues/323
    at = getToolByName(portal, 'archetype_tool')
    at.setCatalogsByType('Attachment', ['portal_catalog'])
    update_arimport_workflow_and_permissions(portal, setup)
    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def update_arimport_workflow_and_permissions(portal, setup):
    """
    Updates the workflow and permissions of ARImprt objects since a new
    workflow has been created for them.
    :param portal: Portal archetype object
    :return: None
    """
    wf_tool = getToolByName(portal, 'portal_workflow')
    logger.info("Updating workflow definitions...")
    wf = wf_tool.getWorkflowById("bika_arimports_workflow")
    wf.updateRoleMappingsFor(setup.arimports)
    logger.info("Workflow definitions updated.")
