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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims import workflow as wf

# Indexes / metadata columns on the parent sample that depend on the
# set of analyses contained in it. They must be refreshed whenever an
# analysis is added to or removed from the sample, otherwise listings
# and catalog queries return stale results until the next workflow
# transition reindexes the sample for other reasons.
SAMPLE_ANALYSIS_DERIVED_IDXS = [
    "getAnalysesKeywords",
    "getAnalysesNum",
    "getProgress",
]


def reindex_parent_analysis_derived(analysis):
    """Reindex the indexes / columns on the parent sample that are
    derived from the analysis set.
    """
    request = analysis.getRequest()
    if request is None:
        return
    request.reindexObject(idxs=SAMPLE_ANALYSIS_DERIVED_IDXS)


def ObjectInitializedEventHandler(analysis, event):
    """Actions to be done when an analysis is added in an Analysis Request
    """
    # Skip temporary analyses that are constructed during new sample creation.
    # This avoids the warning "No workflow provides the '${action_id}' action."
    if api.is_temporary(analysis):
        return

    # Initialize the analysis if it was e.g. added by Manage Analysis
    wf.doActionFor(analysis, "initialize")

    # Try to transition the analysis_request to "sample_received". There are
    # some cases that can end up with an inconsistent state between the AR
    # and the analyses it contains: retraction of an analysis when the state
    # of the AR was "to_be_verified", addition of a new analysis when the
    # state was "to_be_verified", etc.
    request = analysis.getRequest()
    wf.doActionFor(request, "rollback_to_receive")

    # Reindex the indexes for UIDReference fields on creation!
    analysis.reindexObject(idxs="getServiceUID")

    # Refresh sample-level analysis-derived indexes / columns
    reindex_parent_analysis_derived(analysis)
    return


def ObjectRemovedEventHandler(analysis, event):
    """Actions to be done when an analysis is removed from an Analysis Request
    """
    # If all the remaining analyses have been submitted (or verified), try to
    # promote the transition to the Analysis Request
    # Note there is no need to check if the Analysis Request allows a given
    # transition, cause this is already managed by doActionFor
    analysis_request = analysis.getRequest()
    wf.doActionFor(analysis_request, "submit")
    wf.doActionFor(analysis_request, "verify")

    # Refresh sample-level analysis-derived indexes / columns
    reindex_parent_analysis_derived(analysis)
    return
