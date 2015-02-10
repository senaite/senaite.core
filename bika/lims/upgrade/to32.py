from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims.interfaces import IIdServer
from bika.lims import logger

def upgrade(tool):
    """Upgrade to 3.2
    """

    portal = aq_parent(aq_inner(tool))
    siteman = portal.getSiteManager()

    def addIndex(cat, *args):
        try:
            cat.addIndex(*args)
        except:
            pass

    ### update commonly affected tools
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')

    ### Add getParentUID Client level batches (and others)
    # The aim is to remove the getClientUID from the catalog if possible.
    # Even if it isn't yet possible, getParentUID is neater in any place where
    # the value of aq_parent can be other than a Client, to avoid confusion
    bc = getToolByName(portal, 'bika_setup_catalog', None)
    if 'getParentUID' not in bc.indexes():
        bc.addIndex('getParentUID', 'FieldIndex')
    logger.info("Reindex added indexes in bika_setup_catalog")
    bc.manage_reindexIndex(ids=['getParentUID', ])

    ### Remove persistent IIdServer utility - The ID Server was refactored
    siteman.unregisterUtility(provided=IIdServer)
    siteman.utilities.unsubscribe((), IIdServer)
    if IIdServer in siteman.utilities.__dict__['_provided']:
        del siteman.utilities.__dict__['_provided'][IIdServer]
    if IIdServer in siteman.utilities._subscribers[0]:
        del siteman.utilities._subscribers[0][IIdServer]

    ### Add 'BatchUID' index to the bika_analysis_catalog
    # It's going to be a common search field?
    # Used right now for adding Analyses from a Batch to a Worksheet
    bac = getToolByName(portal, 'bika_analysis_catalog')
    addIndex(bac, 'BatchUID', 'FieldIndex')
    bac.manage_reindexIndex(ids=['BatchUID',])

    return True

