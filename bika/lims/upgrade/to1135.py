from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName


class Empty:
    pass


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))

    # then add indexes
    bac = getToolByName(portal, 'bika_analysis_catalog')
    bac.delIndex('getReferenceAnalysesGroupID')
    bac.addIndex('getReferenceAnalysesGroupID', 'FieldIndex')
    try:
        bac.addColumn('getReferenceAnalysesGroupID')
    except:
        pass
    bac.clearFindAndRebuild()
