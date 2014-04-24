from Acquisition import aq_inner
from Acquisition import aq_parent


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # update affected tools
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    return True
