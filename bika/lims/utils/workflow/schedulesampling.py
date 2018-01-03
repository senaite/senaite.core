# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import interfaces
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.browser.bika_listing import WorkflowAction
from bika.lims.workflow import doActionFor
from bika.lims import logger
from bika.lims import bikaMessageFactory as _

SCHEDULE_SAMPLING_TRANSITION_ID = 'schedule_sampling'


def doTransition(obj):
    """
    This function prevent the transition if the fields "SamplingDate"
    and "ScheduledSamplingSampler" are uncompleted.
    :returns: bool, 'an error message'
    """
    errmsg = ''
    if interfaces.ISample.providedBy(obj)\
            or interfaces.IAnalysisRequest.providedBy(obj):
        if obj.getScheduledSamplingSampler() and\
                obj.getSamplingDate():
            doActionFor(obj, SCHEDULE_SAMPLING_TRANSITION_ID)
            return True, 'done'
        msg = _("Missing scheduled sampling sampler or " +
                "sampling date in %s." % obj.getId())
        errmsg = 'missing'
    else:
        msg = _("%s can't be transitioned." % obj.getId())
        errmsg = 'cant_trans'
    logger.warn(msg)
    return False, errmsg
