# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.interfaces.analysis import IRequestAnalysis
from plone.indexer import indexer

@indexer(IAnalysisRequest, IRequestAnalysis)
def cancellation_state(instance):
    """Acts as a mask for cancellation_workflow for those content types that are
    not bound to this workflow. Returns 'active' or 'cancelled'
    """
    if api.get_workflow_status_of(instance) == "cancelled":
        return "cancelled"
    return "active"
