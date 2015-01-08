from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *
from Products.Archetypes.BaseContent import BaseContent
from bika.lims.upgrade import stub


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup

    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')

    stub('bika.lims.content.supplyorderitem', 'SupplyOrderItem',
        BaseContent)
    for order in portal['supplyorders'].objectValues():
        order.supplyorder_lineitems = []
        for soli in order.objectValues():
            item = dict(
                Product=soli.Product,
                Quantity=soli.Quantity,
                Price=soli.Price,
                VAT=soli.VAT,
            )
            order.supplyorder_lineitems.append(item)
    return True
