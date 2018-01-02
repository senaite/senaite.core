# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from DateTime import DateTime

from bika.lims import logger
from bika.lims.utils import changeWorkflowState
from bika.lims.workflow import doActionFor
from bika.lims.workflow import getCurrentState
from bika.lims.workflow import isBasicTransitionAllowed
from bika.lims.workflow import wasTransitionPerformed


def after_submit(obj):
    """
    Method triggered after a 'submit' transition for the Worksheet passed in is
    performed.
    This function is called automatically by
    bika.lims.workfow.AfterTransitionEventHandler
    """
    # Submitting a Worksheet must never transition the analyses.
    # In fact, a worksheet can only be transitioned to "to_be_verified" if
    # all the analyses that contain have been submitted manually after
    # the results input
    doActionFor(obj, 'attach')


def after_verify(obj):
    """Method triggered after a 'verify' transition for the Worksheet
    passed in is performed. Responsible of triggering cascade actions to
    associated analyses.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    :param obj: Worksheet affected by the transition
    :type obj: Worksheet
    """
    pass


def after_retract(obj):
    pass
