from Acquisition import aq_inner
from Acquisition import aq_parent


def upgrade(tool):
    """ Re-import types tool to add condition for sample/partitions view
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
