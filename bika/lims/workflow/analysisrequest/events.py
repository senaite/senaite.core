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
from bika.lims.api.mail import send_email
from bika.lims.api.mail import to_email_attachment
from bika.lims.interfaces import IAnalysisRequestPartition
from bika.lims.interfaces import IDetachedPartition
from bika.lims.interfaces import IReceived
from bika.lims.interfaces import IVerified
from bika.lims.utils import changeWorkflowState
from bika.lims.utils.analysisrequest import create_retest
from bika.lims.workflow import doActionFor as do_action_for
from bika.lims.workflow import get_prev_status_from_history
from bika.lims.workflow.analysisrequest import AR_WORKFLOW_ID
from bika.lims.workflow.analysisrequest import do_action_to_analyses
from bika.lims.workflow.analysisrequest import do_action_to_ancestors
from bika.lims.workflow.analysisrequest import do_action_to_descendants
from DateTime import DateTime
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


def before_sample(analysis_request):
    """Method triggered before "sample" transition for the Analysis Request
    passed in is performed
    """
    if not analysis_request.getDateSampled():
        analysis_request.setDateSampled(DateTime())
    if not analysis_request.getSampler():
        analysis_request.setSampler(api.get_current_user().id)


def after_no_sampling_workflow(analysis_request):
    """Function triggered after "no_sampling_workflow transition for the
    Analysis Request passed in is performed
    """
    setup = api.get_setup()
    if setup.getAutoreceiveSamples():
        # Auto-receive samples is enabled. Note transition to "received" state
        # will only take place if the current user has enough privileges (this
        # is handled by do_action_for already).
        do_action_for(analysis_request, "receive")


def after_reject(analysis_request):
    """Method triggered after a 'reject' transition for the Analysis Request
    passed in is performed. Cascades the transition to descendants (partitions)
    and analyses as well. If "notify on rejection" setting is enabled, sends a
    notification to the client contact.
    """
    do_action_to_descendants(analysis_request, "reject")
    do_action_to_analyses(analysis_request, "reject")


def after_retract(analysis_request):
    """Method triggered after a 'retract' transition for the Analysis Request
    passed in is performed. Cascades the transition to descendants (partitions)
    and analyses as well.
    """
    do_action_to_descendants(analysis_request, "retract")
    do_action_to_analyses(analysis_request, "retract")


def after_invalidate(obj):
    """Function triggered after 'invalidate' transition for the Analysis
    Request passed in is performed. Creates a retest
    """
    create_retest(obj)


def after_submit(analysis_request):
    """Function called after a 'submit' transition is triggered. Promotes the
    submission of ancestors and descendants (partitions).
    """
    # This transition is not meant to be triggered manually by the user, rather
    # promoted by analyses. Hence, there is no need to cascade the transition
    # to the analyses the analysis request contains.
    do_action_to_ancestors(analysis_request, "submit")
    do_action_to_descendants(analysis_request, "submit")


def after_verify(analysis_request):
    """Method triggered after a 'verify' transition for the Analysis Request
    passed in is performed. Promotes the 'verify' transition to ancestors,
    descendants and to the analyses that belong to the analysis request.
    """
    # Mark this analysis request as IReceived
    alsoProvides(analysis_request, IVerified)

    # This transition is not meant to be triggered manually by the user, rather
    # promoted by analyses. Hence, there is no need to cascade the transition
    # to the analyses the analysis request contains.
    do_action_to_ancestors(analysis_request, "verify")
    do_action_to_descendants(analysis_request, "verify")


def after_prepublish(analysis_request):
    """Method triggered after a 'prepublish' transition for the Analysis
    Request passed in is performed. Performs the 'publish' transition to the
    descendant partitions.

    Also see: https://github.com/senaite/senaite.core/pull/1428
    """
    do_action_to_descendants(analysis_request, "publish")


def after_publish(analysis_request):
    """Method triggered after an 'publish' transition for the Analysis Request
    passed in is performed. Performs the 'publish' transition Publishes the
    descendant partitions and all analyses associated to the analysis request
    as well.
    """
    do_action_to_descendants(analysis_request, "publish")
    do_action_to_analyses(analysis_request, "publish")


def after_reinstate(analysis_request):
    """Method triggered after a 'reinstate' transition for the Analysis Request
    passed in is performed. Sets its status to the last status before it was
    cancelled. Reinstates the descendant partitions and all the analyses
    associated to the analysis request as well.
    """
    do_action_to_descendants(analysis_request, "reinstate")
    do_action_to_analyses(analysis_request, "reinstate")

    # Force the transition to previous state before the request was cancelled
    prev_status = get_prev_status_from_history(analysis_request, "cancelled")
    changeWorkflowState(analysis_request, AR_WORKFLOW_ID, prev_status,
                        action="reinstate")
    analysis_request.reindexObject()


def after_cancel(analysis_request):
    """Method triggered after a 'cancel' transition for the Analysis Request
    passed in is performed. Cascades this transition to its analyses and
    partitions.
    """
    do_action_to_descendants(analysis_request, "cancel")
    do_action_to_analyses(analysis_request, "cancel")


def after_receive(analysis_request):
    """Method triggered after "receive" transition for the Analysis Request
    passed in is performed
    """
    # Mark this analysis request as IReceived
    alsoProvides(analysis_request, IReceived)

    analysis_request.setDateReceived(DateTime())
    do_action_to_analyses(analysis_request, "initialize")


def after_sample(analysis_request):
    """Method triggered after "sample" transition for the Analysis Request
    passed in is performed
    """
    analysis_request.setDateSampled(DateTime())


def after_rollback_to_receive(analysis_request):
    """Function triggered after "rollback to receive" transition is performed
    """
    if IVerified.providedBy(analysis_request):
        noLongerProvides(analysis_request, IVerified)


def after_detach(analysis_request):
    """Function triggered after "detach" transition is performed
    """
    # Unbind the sample from its parent (the primary)
    parent = analysis_request.getParentAnalysisRequest()
    analysis_request.setParentAnalysisRequest(None)

    # Assign the primary from which the sample has been detached
    analysis_request.setDetachedFrom(parent)

    # This sample is no longer a partition
    noLongerProvides(analysis_request, IAnalysisRequestPartition)

    # And we mark the sample with IDetachedPartition
    alsoProvides(analysis_request, IDetachedPartition)

    # Reindex both the parent and the detached one
    analysis_request.reindexObject()
    parent.reindexObject()

    # And the analyses too. aranalysesfield relies on a search against the
    # catalog to return the analyses: calling `getAnalyses` to the parent
    # will return all them, so no need to do the same with the detached
    analyses = parent.getAnalyses(full_objects=True)
    map(lambda an: an.reindexObject(), analyses)
