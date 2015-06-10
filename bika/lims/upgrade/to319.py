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
    setup = portal.portal_setup
    # Updated profile steps
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    # important info about upgrade steps in
    # http://stackoverflow.com/questions/7821498/is-there-a-good-reference-list-for-the-names-of-the-genericsetup-import-steps
    setup.runImportStepFromProfile('profile-bika.lims:default', 'skins')
    qi = portal.portal_quickinstaller
    ufrom = qi.upgradeInfo('bika.lims')['installedVersion']
    logger.info("Upgrading Bika LIMS: %s -> %s" % (ufrom, '319'))

    # Migrations

    return True
