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

from zope.interface import alsoProvides

from bika.lims import api
from bika.lims import logger
from bika.lims.interfaces import IDuplicateAnalysis
from bika.lims.interfaces import ISubmitted
from bika.lims.interfaces import IVerified
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims.utils import changeWorkflowState
from bika.lims.utils.analysis import create_analysis
from bika.lims.utils.analysis import create_retest
from bika.lims.workflow import doActionFor
from bika.lims.workflow import push_reindex_to_actions_pool


def after_assign(analysis):
    """Function triggered after an 'assign' transition for the analysis passed
    in is performed.
    """
    reindex_request(analysis)


def before_unassign(analysis):
    """Function triggered before 'unassign' transition takes place
    """
    worksheet = analysis.getWorksheet()
    if not worksheet:
        return

    # Removal of a routine analysis causes the removal of their duplicates
    for dup in worksheet.get_duplicates_for(analysis):
        doActionFor(dup, "unassign")


def before_reject(analysis):
    """Function triggered before 'unassign' transition takes place
    """
    worksheet = analysis.getWorksheet()
    if not worksheet:
        return

    # Rejection of a routine analysis causes the removal of their duplicates
    for dup in worksheet.get_duplicates_for(analysis):
        doActionFor(dup, "unassign")


def after_retest(analysis):
    """Function triggered before 'retest' transition takes place. Creates a
    copy of the current analysis
    """
    # When an analysis is retested, it automatically transitions to verified,
    # so we need to mark the analysis as such
    alsoProvides(analysis, IVerified)

    def verify_and_retest(relative):
        if not ISubmitted.providedBy(relative):
            # Result not yet submitted, no need to create a retest
            return

        # Apply the transition manually, but only if analysis can be verified
        doActionFor(relative, "verify")

        # Create the retest
        create_retest(relative)

    # Retest and auto-verify relatives, from bottom to top
    relatives = list(reversed(analysis.getDependents(recursive=True)))
    relatives.extend(analysis.getDependencies(recursive=True))
    map(verify_and_retest, relatives)

    # Create the retest
    create_retest(analysis)

    # Try to rollback the Analysis Request
    if IRequestAnalysis.providedBy(analysis):
        doActionFor(analysis.getRequest(), "rollback_to_receive")
        reindex_request(analysis)


def after_unassign(analysis):
    """Function triggered after an 'unassign' transition for the analysis passed
    in is performed.
    """
    # Remove from the worksheet
    remove_analysis_from_worksheet(analysis)
    # Reindex the Analysis Request
    reindex_request(analysis)


def after_cancel(analysis):
    """Function triggered after a "cancel" transition is performed. Removes the
    cancelled analysis from the worksheet, if any.
    """
    # Remove from the worksheet
    remove_analysis_from_worksheet(analysis)


def after_reinstate(analysis):
    """Function triggered after a "reinstate" transition is performed.
    """
    pass


def after_submit(analysis):
    """Method triggered after a 'submit' transition for the analysis passed in
    is performed. Promotes the submit transition to the Worksheet to which the
    analysis belongs to. Note that for the worksheet there is already a guard
    that assures the transition to the worksheet will only be performed if all
    analyses within the worksheet have already been transitioned.
    This function is called automatically by
    bika.lims.workfow.AfterTransitionEventHandler
    """
    # Mark this analysis as ISubmitted
    alsoProvides(analysis, ISubmitted)

    # Promote to analyses this analysis depends on
    promote_to_dependencies(analysis, "submit")

    # TODO: REFLEX TO REMOVE
    # Do all the reflex rules process
    if IRequestAnalysis.providedBy(analysis):
        analysis._reflex_rule_process('submit')

    # Promote transition to worksheet
    ws = analysis.getWorksheet()
    if ws:
        doActionFor(ws, 'submit')
        push_reindex_to_actions_pool(ws)

    # Promote transition to Analysis Request
    if IRequestAnalysis.providedBy(analysis):
        doActionFor(analysis.getRequest(), 'submit')
        reindex_request(analysis)


def after_retract(analysis):
    """Function triggered after a 'retract' transition for the analysis passed
    in is performed. The analysis transitions to "retracted" state and a new
    copy of the analysis is created. The copy initial state is "unassigned",
    unless the the retracted analysis was assigned to a worksheet. In such case,
    the copy is transitioned to 'assigned' state too
    """

    # Retract our dependents (analyses that depend on this analysis)
    cascade_to_dependents(analysis, "retract")

    # Retract our dependencies (analyses this analysis depends on)
    promote_to_dependencies(analysis, "retract")

    # Create the retest
    create_retest(analysis)

    # Try to rollback the Analysis Request
    if IRequestAnalysis.providedBy(analysis):
        doActionFor(analysis.getRequest(), "rollback_to_receive")
        reindex_request(analysis)


def after_reject(analysis):
    """Function triggered after the "reject" transition for the analysis passed
    in is performed."""
    # Remove from the worksheet
    remove_analysis_from_worksheet(analysis)

    # Reject our dependents (analyses that depend on this analysis)
    cascade_to_dependents(analysis, "reject")

    if IRequestAnalysis.providedBy(analysis):
        # Try verify (for when remaining analyses are in 'verified')
        doActionFor(analysis.getRequest(), "verify")

        # Try submit (remaining analyses are in 'to_be_verified')
        doActionFor(analysis.getRequest(), "submit")

        # Try rollback (no remaining analyses or some not submitted)
        doActionFor(analysis.getRequest(), "rollback_to_receive")
        reindex_request(analysis)


def after_verify(analysis):
    """
    Method triggered after a 'verify' transition for the analysis passed in
    is performed. Promotes the transition to the Analysis Request and to
    Worksheet (if the analysis is assigned to any)
    This function is called automatically by
    bika.lims.workfow.AfterTransitionEventHandler
    """
    # Mark this analysis as IVerified
    alsoProvides(analysis, IVerified)

    # Promote to analyses this analysis depends on
    promote_to_dependencies(analysis, "verify")

    # TODO: REFLEX TO REMOVE
    # Do all the reflex rules process
    if IRequestAnalysis.providedBy(analysis):
        analysis._reflex_rule_process('verify')

    # Promote transition to worksheet
    ws = analysis.getWorksheet()
    if ws:
        doActionFor(ws, 'verify')
        push_reindex_to_actions_pool(ws)

    # Promote transition to Analysis Request
    if IRequestAnalysis.providedBy(analysis):
        doActionFor(analysis.getRequest(), 'verify')
        reindex_request(analysis)


def after_publish(analysis):
    """Function triggered after a "publish" transition is performed.
    """
    pass


# TODO Workflow - Analysis - revisit reindexing of ancestors
def reindex_request(analysis, idxs=None):
    """Reindex the Analysis Request the analysis belongs to, as well as the
    ancestors recursively
    """
    if not IRequestAnalysis.providedBy(analysis) or \
            IDuplicateAnalysis.providedBy(analysis):
        # Analysis not directly bound to an Analysis Request. Do nothing
        return

    n_idxs = ['assigned_state', 'getDueDate']
    n_idxs = idxs and list(set(idxs + n_idxs)) or n_idxs
    request = analysis.getRequest()
    ancestors = [request] + request.getAncestors(all_ancestors=True)
    for ancestor in ancestors:
        push_reindex_to_actions_pool(ancestor, n_idxs)


def remove_analysis_from_worksheet(analysis):
    """Removes the analysis passed in from the worksheet, if assigned to any
    """
    worksheet = analysis.getWorksheet()
    if not worksheet:
        return

    analyses = filter(lambda an: an != analysis, worksheet.getAnalyses())
    worksheet.setAnalyses(analyses)
    worksheet.purgeLayout()
    if analyses:
        # Maybe this analysis was the only one that was not yet submitted or
        # verified, so try to submit or verify the Worksheet to be aligned
        # with the current states of the analyses it contains.
        doActionFor(worksheet, "submit")
        doActionFor(worksheet, "verify")
    else:
        # We've removed all analyses. Rollback to "open"
        doActionFor(worksheet, "rollback_to_open")

    # Reindex the Worksheet
    idxs = ["getAnalysesUIDs"]
    push_reindex_to_actions_pool(worksheet, idxs=idxs)


def cascade_to_dependents(analysis, transition_id):
    """Cascades the transition to dependent analyses (those that depend on the
    analysis passed in), if any
    """
    for dependent in analysis.getDependents():
        doActionFor(dependent, transition_id)


def promote_to_dependencies(analysis, transition_id):
    """Promotes the transition to the analyses this analysis depends on
    (dependencies), if any
    """
    for dependency in analysis.getDependencies():
        doActionFor(dependency, transition_id)
