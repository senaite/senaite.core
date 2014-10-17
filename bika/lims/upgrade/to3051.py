from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import *
from bika.lims.setuphandlers import BikaGenerator
from bika.lims import logger

def upgrade(tool):
    """ Adding getRawSamplePoint/Type idx to obtain Sample's uid easly
    """
    portal = aq_parent(aq_inner(tool))
    bsc = getToolByName(portal, 'bika_setup_catalog', None)

    if 'getRawSamplePoints' not in bsc.indexes():
        bsc.addIndex('getRawSamplePoints', 'KeywordIndex')
    if 'getRawSampleTypes' not in bsc.indexes():
        bsc.addIndex('getRawSampleTypes', 'KeywordIndex')

    logger.info("Reindex added indexes in bika_setup_catalog")
    bsc.manage_reindexIndex(ids=['getRawSamplePoints', ])
    bsc.manage_reindexIndex(ids=['getRawSampleTypes', ])

    return True
