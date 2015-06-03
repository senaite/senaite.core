from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *


def upgrade(tool):
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))

    # missing /supplyorders folder permission
    clients = portal.clients.objectValues()
    for client in clients:
        mp = client.manage_permission
        mp(AddSupplyOrder, ['Manager', 'LabManager', 'Owner'], 0)
        client.reindexObject()

    return True
