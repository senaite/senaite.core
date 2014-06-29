from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore import permissions


def upgrade(tool):
    """LIMS-1275 - Remove acquisition for "Modify portal content" permission
    """
    portal = aq_parent(aq_inner(tool))

    # /bika_setup -
    mp = portal.bika_setup.manage_permission
    mp(permissions.ModifyPortalContent, ['Manager', 'LabManager'], 0)
    portal.batches.reindexObject()

    return True
