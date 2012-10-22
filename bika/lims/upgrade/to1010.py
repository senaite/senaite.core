##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import logging

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent

from Products.CMFCore.utils import getToolByName

def to1010(tool):
    """
    """
    portal = aq_parent(aq_inner(tool))
    portal_catalog = getoToolByName(portal, 'portal_catalog')

    # add BatchID to all AnalysisRequest objects.
    # When the objects are reindexed, BatchUID will also be populated
    proxies = portal_catalog(portal_type="AnalysiRequest")
    ars = (proxy.getObject() for proxy in proxies)
    for ar in ars:
        ar.setBatchID(None)

    return False

