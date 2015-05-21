from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.Archetypes.BaseContent import BaseContent
from bika.lims.upgrade import stub


def upgrade(tool):
    """Upgrade step required for Bika LIMS 3.1.8
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # Updated profile steps
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')

    # Migrations

    return True
