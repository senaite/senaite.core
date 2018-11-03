# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.workflow.analysis.guards import guard_submit as base_submit


def guard_submit(reference_analysis):
    """Return whether the transition "submit" can be performed or not
    """
    return base_submit(reference_analysis)
