from Acquisition import aq_inner
from Acquisition import aq_parent


def upgrade(tool):
    """ Insert CSV workflow definitions
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow-csv')
