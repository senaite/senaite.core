from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    wf = portal.portal_workflow

    setup.runImportStepFromProfile('profile-bika.lims:default', 'workflow')

    wf.updateRoleMappings()

    return True
