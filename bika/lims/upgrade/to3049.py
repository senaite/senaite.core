from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import *
from bika.lims.setuphandlers import BikaGenerator
from bika.lims import logger

def upgrade(tool):
    """ Sort by Type in instruments
    """
    portal = aq_parent(aq_inner(tool))

    bsc = getToolByName(portal, 'bika_setup_catalog', None)
    bsc.addIndex('getInstrumentType', 'FieldIndex')
    bsc.addColumn('getInstrumentType')

    #Del old "getType" Index, it's not used now.
    if 'getType' in bsc.indexes():
        bsc.delIndex('getType')
    if 'getType' in bsc.indexes():
        bsc.delColumn('getType')

    setup = portal.portal_setup

    bsc.clearFindAndRebuild()
    return True
