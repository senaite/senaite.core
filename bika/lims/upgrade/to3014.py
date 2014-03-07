from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))

    # missing /supplyorders folder permission
    clients = portal.clients.objectValues()
    for client in clients:
        mp = client.manage_permission
        mp(AddSupplyOrder, ['Manager', 'LabManager', 'Owner'], 0)
        client.reindexObject()

    return True
