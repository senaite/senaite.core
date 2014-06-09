from Acquisition import aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName

def upgrade(tool):
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
