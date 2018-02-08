# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException

from bika.lims import logger
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
    return isBasicTransitionAllowed(obj)


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
                    sp_wf_name)
        return False

    # get state from workflow - error = allow transition
    # get possible exit transitions for state: error = allow transition
    transitions = sp_wf
    if len(transitions) > 0:
        return False
    return True
