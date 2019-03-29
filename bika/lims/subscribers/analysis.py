# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import workflow as wf


def ObjectInitializedEventHandler(analysis, event):
    """Actions to be done when an analysis is added in an Analysis Request
    """

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
    return
