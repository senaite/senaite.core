from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *


def upgrade(tool):
    """Added bika.lims.client.view.js
    """

    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # reread jsregistry with the new data
    setup.runImportStepFromProfile('profile-bika.lims:default', 'jsregistry')

    return True
