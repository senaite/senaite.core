from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims import logger
from bika.lims.permissions import *
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest


def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    portal_catalog = getToolByName(portal, 'portal_catalog')

    proxies = portal_catalog(portal_type="AnalysisRequest")
    ars = [proxy.getObject() for proxy in proxies]
    for ar in ars:
        if not ar.getPriority():
            ar.setDefaultPriority()


    return True
