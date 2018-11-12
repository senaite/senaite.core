# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import transaction
from Products.CMFCore.utils import getToolByName

from bika.lims import logger
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims.utils.analysis import create_analysis
from bika.lims.workflow import doActionFor
from bika.lims.workflow import skip


def after_assign(analysis):
    """Function triggered after an 'assign' transition for the analysis passed
    in is performed.
    """
    pass


def after_unassign(analysis):
    """Function triggered after an 'unassign' transition for the analysis passed
    in is performed.
    """
    request = analysis.getRequest()
    request.reindexObject(idxs=["assigned_state"])

def after_submit(analysis):
    """Method triggered after a 'submit' transition for the analysis passed in
    is performed. Promotes the submit transition to the Worksheet to which the
    analysis belongs to. Note that for the worksheet there is already a guard
    that assures the transition to the worksheet will only be performed if all
    analyses within the worksheet have already been transitioned.
    This function is called automatically by
    bika.lims.workfow.AfterTransitionEventHandler
    """
    # Promote to analyses this analysis depends on
    for dependency in analysis.getDependencies():
        doActionFor(dependency, "submit")

    # TODO: REFLEX TO REMOVE
    # Do all the reflex rules process
    if IRequestAnalysis.providedBy(analysis):
        analysis._reflex_rule_process('submit')

    # Promote transition to worksheet
    ws = analysis.getWorksheet()
    if ws:
        doActionFor(ws, 'submit')

    # Promote transition to Analysis Request
    if IRequestAnalysis.providedBy(analysis):
        doActionFor(analysis.getRequest(), 'submit')


def after_retract(obj):
    """Function triggered after a 'retract' transition for the analysis passed
    in is performed. Retracting an analysis cause its transition to 'retracted'
    state and the creation of a new copy of the same analysis as a retest.
    Note that retraction only affects to single Analysis and has no other
    effect in the status of the Worksheet to which the Analysis is assigned or
    to the Analysis Request to which belongs (transition is never proomoted)
    This function is called automatically by
    bika.lims.workflow.AfterTransitionEventHandler
    """
    # TODO Workflow Analysis - review this function
    # Rename the analysis to make way for it's successor.
    # Support multiple retractions by renaming to *-0, *-1, etc
    parent = obj.aq_parent
    kw = obj.getKeyword()
    analyses = [x for x in parent.objectValues("Analysis")
                if x.getId().startswith(obj.getId())]

    # LIMS-1290 - Analyst must be able to retract, which creates a new
    # Analysis.  So, _verifyObjectPaste permission check must be cancelled:
    parent._verifyObjectPaste = str
    # This is needed for tests:
    # https://docs.plone.org/develop/plone/content/rename.html
    # Testing warning: Rename mechanism relies of Persistent attribute
    # called _p_jar to be present on the content object. By default, this is
    # not the case on unit tests. You need to call transaction.savepoint() to
    # make _p_jar appear on persistent objects.
    # If you don't do this, you'll receive a "CopyError" when calling
    # manage_renameObjects that the operation is not supported.
    transaction.savepoint()
    parent.manage_renameObject(kw, "{0}-{1}".format(kw, len(analyses)))
    delattr(parent, '_verifyObjectPaste')

    # Create new analysis from the retracted obj
    analysis = create_analysis(parent, obj)

    # Assign the new analysis to this same worksheet, if any.
    ws = obj.getWorksheet()
    if ws:
        ws.addAnalysis(analysis)
    analysis.reindexObject()

    # retract our dependencies
    dependencies = obj.getDependencies()
    for dependency in dependencies:
        doActionFor(dependency, 'retract')

    # Retract our dependents
    dependents = obj.getDependents()
    for dependent in dependents:
        doActionFor(dependent, 'retract')

    _reindex_request(obj)


def after_verify(analysis):
    """
    Method triggered after a 'verify' transition for the analysis passed in
    is performed. Promotes the transition to the Analysis Request and to
    Worksheet (if the analysis is assigned to any)
    This function is called automatically by
    bika.lims.workfow.AfterTransitionEventHandler
    """

    # Promote to analyses this analysis depends on
    for dependency in analysis.getDependencies():
        doActionFor(dependency, 'verify')

    # TODO: REFLEX TO REMOVE
    # Do all the reflex rules process
    if IRequestAnalysis.providedBy(analysis):
        analysis._reflex_rule_process('verify')

    # Promote transition to worksheet
    ws = analysis.getWorksheet()
    if ws:
        doActionFor(ws, 'verify')

    # Promote transition to Analysis Request
    if IRequestAnalysis.providedBy(analysis):
        doActionFor(analysis.getRequest(), 'verify')


def after_cancel(obj):
    if skip(obj, "cancel"):
        return
    # If it is assigned to a worksheet, unassign it.
    worksheet = obj.getWorksheet()
    if worksheet:
        worksheet.removeAnalysis(obj)
    obj.reindexObject()
    _reindex_request(obj)


def after_reject(obj):
    if skip(obj, "reject"):
        return
    # If it is assigned to a worksheet, unassign it.
    worksheet = obj.getWorksheet()
    if worksheet:
        worksheet.removeAnalysis(obj)
    obj.reindexObject()
    _reindex_request(obj)


def after_attach(obj):
    if skip(obj, "attach"):
        return
    workflow = getToolByName(obj, "portal_workflow")
    # If all analyses in this AR have been attached escalate the action
    # to the parent AR
    ar = obj.aq_parent
    state = workflow.getInfoFor(ar, "review_state")
    if state == "attachment_due" and not skip(ar, "attach", peek=True):
        can_attach = True
        for a in ar.getAnalyses():
            if a.review_state in ("unassigned", "assigned", "attachment_due"):
                can_attach = False
                break
        if can_attach:
            workflow.doActionFor(ar, "attach")
    # If assigned to a worksheet and all analyses on the worksheet have
    # been attached, then attach the worksheet.
    ws = obj.getWorksheet()
    if ws:
        ws_state = workflow.getInfoFor(ws, "review_state")
        if ws_state == "attachment_due" \
                and not skip(ws, "attach", peek=True):
            can_attach = True
            for a in ws.getAnalyses():
                state = workflow.getInfoFor(a, "review_state")
                if state in ("unassigned", "assigned", "attachment_due"):
                    can_attach = False
                    break
            if can_attach:
                workflow.doActionFor(ws, "attach")
    obj.reindexObject()
    _reindex_request(obj)


def _reindex_request(obj, idxs=None):
    if not IRequestAnalysis.providedBy(obj):
        return
    request = obj.getRequest()
    if idxs is None:
        request.reindexObject()
    else:
        request.reindexObject(idxs=idxs)
