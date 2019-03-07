# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.workflow.analysis import guards as analysis_guards


def guard_submit(reference_analysis):
    """Return whether the transition "submit" can be performed or not
    """
    return analysis_guards.guard_submit(reference_analysis)


def guard_multi_verify(duplicate_analysis):
    """Return whether the transition "multi_verify" can be performed or not
    """
    return analysis_guards.guard_multi_verify(duplicate_analysis)


def guard_verify(reference_analysis):
    """Return whether the transition "verify" can be performed or not
    """
    return analysis_guards.guard_verify(reference_analysis)


def guard_unassign(reference_analysis):
    """Return whether the transition 'unassign' can be performed or not
    """
    return analysis_guards.guard_unassign(reference_analysis)


def guard_retract(duplicate_analysis):
    """Return whether the transition 'retract' can be performed or not
    """
    return analysis_guards.guard_retract(duplicate_analysis)
