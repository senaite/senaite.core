from Acquisition import aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName

def upgrade(tool):
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))

    # Fix Pricelists - VATTotal was renamed to VATAmount
    pc = getToolByName(portal, "portal_catalog")
    items = pc(portal_type="Pricelist")
    for proxy in items:
        pl = proxy.getObject()
        new = []
        for li in pl.pricelist_lineitems:
            if 'VATTotal' in li:
                li['VATAmount'] = li['VATTotal']
                del(li['VATTotal'])
        new.append(li)
        pl.pricelist_lineitems = new

    return True
