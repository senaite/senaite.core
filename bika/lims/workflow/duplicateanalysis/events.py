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
from bika.lims.workflow.analysis import events as analysis_events


def after_submit(obj):
    """Method triggered after a 'submit' transition for the duplicate analysis
    passed in is performed.
    Delegates to bika.lims.workflow.analysis.events.after_submit
    This function is called automatically by
    bika.lims.workfow.AfterTransitionEventHandler
    """
    analysis_events.after_submit(obj)


def after_verify(obj):
    """Method triggered after a 'verify' transition for the duplicate analysis
    passed in is performed. Promotes the transition to its parent worksheet,
    but the worksheet will only be transitioned to 'verified' if all its
    analyses have been previously verified. See the Worksheet's verify guard
    for further information.
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    """
    # Ecalate to Worksheet. Note that the guard for verify transition from
    # Worksheet will check if the Worksheet can be transitioned, so there is no
    # need to check here if all analyses within the WS have been transitioned
    # already
    ws = obj.getWorksheet()
    if ws:
        doActionFor(ws, 'verify')


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
