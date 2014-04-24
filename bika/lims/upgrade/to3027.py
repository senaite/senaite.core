from Acquisition import aq_inner
from Acquisition import aq_parent


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))

    portal.portal_actions.portal_tabs.queries.visible = False

    return True
