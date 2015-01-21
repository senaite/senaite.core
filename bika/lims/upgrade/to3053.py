from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.interfaces import IIdServer


def upgrade(tool):
    """ Remove persistent IIdServer utility
    """
    portal = aq_parent(aq_inner(tool))
    sm = portal.getSiteManager()
    sm.unregisterUtility(provided=IIdServer)
    sm.utilities.unsubscribe((), IIdServer)
    if IIdServer in sm.utilities.__dict__['_provided']:
        del sm.utilities.__dict__['_provided'][IIdServer]
    if IIdServer in sm.utilities._subscribers[0]:
        del sm.utilities._subscribers[0][IIdServer]

    return True

