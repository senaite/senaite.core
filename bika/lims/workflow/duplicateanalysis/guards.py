# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

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
