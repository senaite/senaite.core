from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))

    for pricelist in portal.pricelists.objectValues('Pricelist'):
        for broken in pricelist.objectValues('PriceListLineItem'):
            pricelist.manage_delObjects([broken.id])

    pc = getToolByName(portal, 'portal_catalog')
    pc.refreshCatalog(clear=1)

    return True
