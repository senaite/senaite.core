# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import logger
from bika.lims.workflow import doActionFor
from bika.lims.workflow.analysis import events as analysis_events


def after_submit(duplicate_analysis):
    """Method triggered after a 'submit' transition for the duplicate analysis
    passed in is performed.
    Delegates to bika.lims.workflow.analysis.events.after_submit
    """
    analysis_events.after_submit(duplicate_analysis)


def after_verify(duplicate_analysis):
    """Function called after a 'verify' transition for the duplicate analysis
    passed in is performed
    Delegates to bika.lims.workflow.analysis.events.after_verify
    """
    analysis_events.after_verify(duplicate_analysis)


def after_unassign(duplicate_analysis):
    """Removes the duplicate from the system
    """
    worksheet = duplicate_analysis.getWorksheet()
    worksheet.manage_delObjects(duplicate_analysis.getId())


def after_retract(obj):
    """Method triggered after a 'retract' transition for the duplicate analysis
    passed in is performed. Retracting an analysis cause its transition to
    'retracted'
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    """
    # TODO Workflow Duplicate Retraction - The current duplicate must be
    # retracted and a new copy of the duplicate for rested must be created.
    # Retracting an analysis must never have any effect to the Worksheet
    pass


def after_attach(obj):
    # TODO Workflow Duplicate Attach - Attach transition is still available?
    # If all analyses on the worksheet have been attached,
    # then attach the worksheet.
    ws = obj.getWorksheet()
    if ws:
        doActionFor(ws)
