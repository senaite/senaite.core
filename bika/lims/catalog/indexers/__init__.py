# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims.interfaces import ICancellable, IDeactivable
from plone.indexer import indexer

@indexer(ICancellable)
def cancellation_state(instance):
    """Acts as a mask for cancellation_workflow for those content types that are
    not bound to this workflow. Returns 'active' or 'cancelled'
    """
    if api.get_workflow_status_of(instance) == "cancelled":
        return "cancelled"
    return "active"


@indexer(IDeactivable)
def inactive_state(instance):
    """Acts as a mask for inactive_wrofklow for those content types that are not
    bound to this workflow. Returns 'active' or 'inactive'
    """
    if api.get_workflow_status_of(instance) == "inactive":
        return "inactive"
    return "active"
