from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    """ Just some catalog indexes to update
    """
    portal = aq_parent(aq_inner(tool))
    portal_catalog = getToolByName(portal, 'portal_catalog')
    typestool = getToolByName(portal, 'portal_types')
    setup = portal.portal_setup

    bc = getToolByName(portal, 'bika_catalog')
    bc.delIndex('getSampleTypeTitle')
    bc.delIndex('getSamplePointTitle')
    bc.addIndex('getSampleTypeTitle', 'KeywordIndex')
    bc.addIndex('getSamplePointTitle', 'KeywordIndex')
    bc.clearFindAndRebuild()
