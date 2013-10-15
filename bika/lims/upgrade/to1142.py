from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims.permissions import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName


class Empty:
    pass


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    pc = getToolByName(portal, 'portal_catalog')
    addIndexAndColumn(pc, 'getParentUID', 'FieldIndex')
    pc.clearFindAndRebuild()


def addIndexAndColumn(catalog, index, indextype):
    try:
        catalog.addIndex(index, indextype)
    except:
        pass
    try:
        catalog.addColumn(index)
    except:
        pass

