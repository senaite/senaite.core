from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from bika.lims import logger


def upgrade(tool):
    """ Add getParentUID Client level batches (and others)

    - The aim is to remove the getClientUID from the catalog if possible.
      Even if it isn't yet possible, getParentUID is neater in any place where
      the value of aq_parent can be other than a Client, to avoid confusion in
      code.

    """
    portal = aq_parent(aq_inner(tool))

    # update affected tools
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')

    # add getParentUID index
    bc = getToolByName(portal, 'bika_setup_catalog', None)
    if 'getParentUID' not in bc.indexes():
        bc.addIndex('getParentUID', 'FieldIndex')
    logger.info("Reindex added indexes in bika_setup_catalog")
    bc.manage_reindexIndex(ids=['getParentUID', ])

    return True

