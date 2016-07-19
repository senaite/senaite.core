from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.permissions import AddMultifile
from Products.Archetypes.BaseContent import BaseContent
from bika.lims.upgrade import stub
from bika.lims import logger


def upgrade(tool):
    """Upgrade step required for Pharmaway report
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    # Adding indexes
    pc = getToolByName(portal, 'portal_catalog', None)
    if 'getClientUID' not in pc.indexes():
        pc.addIndex('getClientUID', 'FieldIndex')
    if 'getSampleTypeUID' not in pc.indexes():
        pc.addIndex('getSampleTypeUID', 'FieldIndex')
    if 'getDateSampled' not in pc.indexes():
        pc.addIndex('getDateSampled', 'FieldIndex')
    pc.manage_reindexIndex(ids=[
        'getClientUID',
        'getSampleTypeUID',
        'getDateSampled'])
    logger.info("Reindex added indexes in portal_catalog")

    return True
