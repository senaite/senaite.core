from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore import permissions


def upgrade(tool):
    """LIMS-1275 - Remove acquisition for "Modify portal content" permission
    """
    # Hack prevent out-of-date upgrading
    # Related: PR #1484
    # https://github.com/bikalabs/Bika-LIMS/pull/1484
    from bika.lims.upgrade import skip_pre315
    if skip_pre315(aq_parent(aq_inner(tool))):
        return True

    portal = aq_parent(aq_inner(tool))

    # /bika_setup -
    mp = portal.bika_setup.manage_permission
    mp(permissions.ModifyPortalContent, ['Manager', 'LabManager'], 0)
    portal.batches.reindexObject()

    return True
