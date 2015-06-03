from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName

def upgrade(tool):
    """ Refactor ARs listing to allow sorting by priority
    """
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True


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
    bc.manage_reindexIndex(ids=['Priority', 'BatchUID',])

    bac = getToolByName(portal, 'bika_analysis_catalog')
    addIndex(bac, 'Priority', 'FieldIndex')
    bac.manage_reindexIndex(ids=['Priority',])

    return True
