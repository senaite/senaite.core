from Acquisition import aq_inner
from Acquisition import aq_parent
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

    # Migrations

    return True
