# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.workflow.analysis import events as analysis_events


def after_submit(obj):
    """Method triggered after a 'submit' transition for the reference analysis
    passed in is performed.
    Delegates to bika.lims.workflow.analysis.events.after_submit
    """
    analysis_events.after_submit(obj)
