# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.Archetypes.interfaces import IBaseObject
from bika.lims import api
from bika.lims.interfaces import ICancellable, IDeactivable
from plone.indexer import indexer


@indexer(ICancellable)
def cancellation_state(instance):
    """Returns "cancelled" or "active"
    """
    if api.get_workflow_status_of(instance) == "cancelled":
        return "cancelled"
    return "active"


@indexer(IDeactivable)
def inactive_state(instance):
    """Returns "inactive" or "active"
    """
    if api.get_workflow_status_of(instance) == "inactive":
        return "inactive"
    return "active"


@indexer(IBaseObject)
def is_active(instance):
    """Returns False if the status of the instance is 'cancelled' or 'inactive'.
    Otherwise returns True
    """
    return api.get_review_status(instance) not in ["cancelled", "inactive"]
