# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.workflow.analysis import events as analysis_events


def after_submit(reference_analysis):
    """Method triggered after a 'submit' transition for the reference analysis
    passed in is performed.
    Delegates to bika.lims.workflow.analysis.events.after_submit
    """
    analysis_events.after_submit(reference_analysis)


def after_verify(reference_analysis):
    """Function called after a 'verify' transition for the reference analysis
    passed in is performed
    Delegates to bika.lims.workflow.analysis.events.after_verify
    """
    analysis_events.after_verify(reference_analysis)


def after_unassign(reference_analysis):
    """Removes the reference analysis from the system
    """
    ref_sample = reference_analysis.aq_parent
    ref_sample.manage_delObjects([reference_analysis.getId()])
