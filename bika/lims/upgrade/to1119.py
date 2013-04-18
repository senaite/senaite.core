from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName


def upgrade(tool):
    """ https://github.com/bikalabs/Bika-LIMS/issues/759
    """
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    mp = portal.clients.manage_permission

    mp('Add portal content', ['Analyst'], 1)

    return True
