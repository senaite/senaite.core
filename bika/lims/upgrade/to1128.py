from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName


class Empty:
    pass


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    typestool = getToolByName(portal, 'portal_types')

    # Add new indexes
    pc = getToolByName(portal, 'portal_catalog')
    if 'getClientSampleID' not in pc.indexes():
        pc.addIndex('getClientSampleID', 'FieldIndex')
    pc.addColumn('getClientSampleID')
    pc.clearFindAndRebuild()

    return True
