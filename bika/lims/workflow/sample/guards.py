# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName

from bika.lims import logger
from bika.lims.workflow import getCurrentState
from bika.lims.workflow import isBasicTransitionAllowed


def schedule_sampling(obj):
    """
    Prevent the transition if:
    - if the user isn't part of the sampling coordinators group
      and "sampling schedule" checkbox is set in bika_setup
    - if no date and samples have been defined
      and "sampling schedule" checkbox is set in bika_setup
    """
    if obj.bika_setup.getScheduleSamplingEnabled() and \
            isBasicTransitionAllowed(obj):
        return True
    return False


def receive(obj):
    """This transition can be fired from 'registered' and 'due' states, and
    the result depends on the SamplingWorkflow and AutoReceiveSamples settings:
    +==================+=============+=============+==============+
    | SamplingWorkflow |   State     | AutoReceive | Guard result |
    +==================+=============+=============+==============+
    | Enabled          | registered  | Enabled     | False        |
    | Enabled          | registered  | Disabled    | False        |
    | Enabled          | due         | Enabled     | True         |
    | Enabled          | due         | Disabled    | False        |
    | Disabled         | registered  | Enabled     | True         |
    | Disabled         | registered  | Disabled    | False        |
    +==================+=============+=============+==============+
    """
    if not isBasicTransitionAllowed(obj):
        return False

    sw = obj.SamplingWorkflowEnabled()
    st = getCurrentState(obj)
    ar = obj.bika_setup.getAutoReceiveSamples()

    if [sw, st, ar] == [True, 'sample_registered', True]:
        return False
    if [sw, st, ar] == [True, 'sample_registered', False]:
        return False
    if [sw, st, ar] == [True, 'sample_due', True]:
        return True
    if [sw, st, ar] == [True, 'sample_due', False]:
        return False
    if [sw, st, ar] == [False, 'sample_registered', True]:
        return True


def sample_prep(obj):
    """Allow the sampleprep automatic transition to fire.
    """
    if not isBasicTransitionAllowed(obj):
        return False
    return obj.getPreparationWorkflow()


def sample_prep_complete(obj):
    """ This relies on user created workflow.  This function must
    defend against user errors.

    AR and Analysis guards refer to this one.

    - If error is encountered, do not permit object to proceed.  Break
      this rule carelessly and you may see recursive automatic workflows.

    - If sampleprep workflow is badly configured, primary review_state
      can get stuck in "sample_prep" forever.

    """
    wftool = getToolByName(obj, 'portal_workflow')
    try:
        # get sampleprep workflow object.
        sp_wf_name = obj.getPreparationWorkflow()
        sp_wf = wftool.getWorkflowById(sp_wf_name)
        # get sampleprep_review state.
        sp_review_state = wftool.getInfoFor(obj, 'sampleprep_review_state')
        assert sp_review_state
    except WorkflowException as e:
        logger.warn("guard_sample_prep_complete_transition: "
                    "WorkflowException %s" % e)
        return False
    except AssertionError:
        logger.warn("'%s': cannot get 'sampleprep_review_state'" %
                    sampleprep_wf_name)
        return False

    # get state from workflow - error = allow transition
    # get possible exit transitions for state: error = allow transition
    transitions = sp_wf
    if len(transitions) > 0:
        return False
    return True
