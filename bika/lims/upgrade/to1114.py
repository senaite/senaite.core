from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    """ Adds the Published Results Tab inside AR View
    """
    portal = aq_parent(aq_inner(tool))
    portal_catalog = getToolByName(portal, 'portal_catalog')
    typestool = getToolByName(portal, 'portal_types')
    setup = portal.portal_setup

    # Reimport Types Tool to add Published Results View inside AR
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')