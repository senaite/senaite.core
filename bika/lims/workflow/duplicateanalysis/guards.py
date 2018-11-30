# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims import workflow as wf
from bika.lims.workflow.analysis import guards as analysis_guards


def guard_submit(duplicate_analysis):
    """Return whether the transition "submit" can be performed or not
    """
    return analysis_guards.guard_submit(duplicate_analysis)


def guard_multi_verify(duplicate_analysis):
    """Return whether the transition "multi_verify" can be performed or not
    """
    return analysis_guards.guard_multi_verify(duplicate_analysis)


def guard_verify(duplicate_analysis):
    """Return whether the transition "verify" can be performed or not
    """
    return analysis_guards.guard_verify(duplicate_analysis)


def guard_unassign(duplicate_analysis):
    """Return whether the transition 'unassign' can be performed or not
    """
    analysis = duplicate_analysis.getAnalysis()
    if wf.isTransitionAllowed(analysis, "unassign"):
        return True
    skip = ["retracted", "rejected", "unassigned"]
    if api.get_review_status(analysis) in skip:
        return True
    return analysis_guards.guard_unassign(duplicate_analysis)


def guard_retract(duplicate_analysis):
    """Return whether the transition 'retract' can be performed or not
    """
    return analysis_guards.guard_retract(duplicate_analysis)
