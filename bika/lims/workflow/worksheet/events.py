# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import workflow as wf


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
    wf.doActionFor(obj, 'attach')


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


def after_rollback_to_receive(analysis_request):
    """Function triggered after rollback_to_receive transition finishes
    """
    pass
