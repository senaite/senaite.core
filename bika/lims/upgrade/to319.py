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

    qi = portal.portal_quickinstaller
    ufrom = qi.upgradeInfo('bika.lims')['installedVersion']
    logger.info("Upgrading Bika LIMS: %s -> %s" % (ufrom, '319'))

    # Migrations

    return True
