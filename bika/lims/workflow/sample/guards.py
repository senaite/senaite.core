# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException

from bika.lims import logger
from bika.lims.workflow import isBasicTransitionAllowed, getCurrentState


def schedule_sampling(obj):
    """
    Prevent the transition if:
    - if the user isn't part of the sampling coordinators group
      and "sampling schedule" checkbox is set in bika_setup
    - if no date and samples have been defined
      and "sampling schedule" checkbox is set in bika_setup
    """
    if obj.bika_setup.getScheduleSamplingEnabled() and \
            isBasicTransitionAllowed(obj):
        return True
    return False


def receive(obj):
    if not isBasicTransitionAllowed(obj):
        return False

    # XXX This conflicts with the sample/events.py/after_sample handler.
    # In that case, "sampled" state may prefer "sample_due" to "receive".
    if getCurrentState(obj) != 'sample_registered':
        return True
    if obj.getSamplingWorkflowEnabled():
        return False
    return obj.bika_setup.getAutoReceiveSamples()
