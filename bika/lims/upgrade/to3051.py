from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import *
from bika.lims.setuphandlers import BikaGenerator
from bika.lims import logger

def upgrade(tool):
    """ Adding getRawSamplePoint idx to obtain SamplePint's uid easly
    """
    portal = aq_parent(aq_inner(tool))
    bsc = getToolByName(portal, 'bika_setup_catalog', None)

    if 'getRawSamplePoints' not in bsc.indexes():
        bsc.addIndex('getRawSamplePoints', 'KeywordIndex')

    bsc.clearFindAndRebuild()
    return True
