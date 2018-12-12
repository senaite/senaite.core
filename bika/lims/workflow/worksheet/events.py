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
