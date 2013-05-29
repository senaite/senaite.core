from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *


def upgrade(tool):
    """We have uids *and* titles for ARTemplate containers and preservations.
    Populate title subfields here.
    """
    portal = aq_parent(aq_inner(tool))
    bsc = portal.bika_setup_catalog

    for p in bsc(portal_type='ARTemplate'):
        o = p.getObject()
        parts = o.getPartitions()
        for i, part in enumerate(parts):
            if 'container_uid' in part:
                container = bsc(portal_type='Container',
                                UID=part['container_uid'])
                if container:
                    container = container[0].getObject()
                    parts[i]['Container'] = container.Title()
            if 'preservation_uid' in p:
                preservation = bsc(portal_type='Preservation',
                                   UID=part['preservation_uid'])
                if preservation:
                    preservation = preservation[0].getObject()
                    parts[i]['Preservation'] = preservation.Title()

    return True
