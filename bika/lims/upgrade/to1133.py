from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName


class Empty:
    pass


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    bac = getToolByName(portal, 'bika_analysis_catalog')
    if 'getReferenceAnalysesGroupID' not in bac.indexes():
        bac.addIndex('getReferenceAnalysesGroupID', 'FieldIndex')
    bac.addColumn('getReferenceAnalysesGroupID')
    bac.clearFindAndRebuild()
    return True
