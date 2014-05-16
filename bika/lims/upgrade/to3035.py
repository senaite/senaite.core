from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.config import REFERENCE_CATALOG

def upgrade(tool):
    """ Refactor ARs listing to allow sorting by priority
    """

    def addIndex(cat, *args):
        try:
            cat.addIndex(*args)
        except:
            pass

    portal = aq_parent(aq_inner(tool))
    # Create new indexes
    bc = getToolByName(portal, 'bika_catalog')
    addIndex(bc, 'Priority', 'FieldIndex')
    addIndex(bc, 'BatchUID', 'FieldIndex')
    bc.clearFindAndRebuild()

    bac = getToolByName(portal, 'bika_analysis_catalog')
    addIndex(bac, 'Priority', 'FieldIndex')
    bac.clearFindAndRebuild()

    return True
