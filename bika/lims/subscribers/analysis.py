# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from AccessControl import getSecurityManager
from Acquisition import aq_inner
from bika.lims import logger
from bika.lims.subscribers import doActionFor
from bika.lims.subscribers import skip
from bika.lims.utils import changeWorkflowState
from DateTime import DateTime
from Products.Archetypes.config import REFERENCE_CATALOG
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
import transaction
import zope.event
from zope.interface import alsoProvides


def ObjectInitializedEventHandler(instance, event):

    wf_tool = getToolByName(instance, 'portal_workflow')

    ar = instance.getRequest()
    ar_state = wf_tool.getInfoFor(ar, 'review_state')

    # Set the state of the analysis depending on the state of the AR.
    if ar_state in ('sample_registered',
                    'to_be_sampled',
                    'sampled',
                    'to_be_preserved',
                    'sample_due',
                    'sample_received'):
        changeWorkflowState(instance, "bika_analysis_workflow", ar_state)
    elif ar_state in ('to_be_verified'):
        # Apply to AR only; we don't want this transition to cascade.
        if 'workflow_skiplist' not in ar.REQUEST:
            ar.REQUEST['workflow_skiplist'] = []
        ar.REQUEST['workflow_skiplist'].append("retract all analyses")
        wf_tool.doActionFor(ar, 'retract')
        ar.REQUEST['workflow_skiplist'].remove("retract all analyses")

    return

def ObjectRemovedEventHandler(instance, event):
    # TODO Workflow - Review all this function and normalize
    # May need to promote the AR's review_state
    # if all other analyses are at a higher state than this one was.
    workflow = getToolByName(instance, 'portal_workflow')
    ar = instance.getRequest()
    can_submit = True
    can_attach = True
    can_verify = True
    can_publish = True

    # We add this manually here, because during admin/ZMI removal,
    # it may possibly not be added by the workflow code.
    if not 'workflow_skiplist' in instance.REQUEST:
        instance.REQUEST['workflow_skiplist'] = []

    for a in ar.getAnalyses():
        a_state = a.review_state
        if a_state in \
           ('to_be_sampled', 'to_be_preserved',
            'sample_due', 'sample_received',):
            can_submit = False
        if a_state in \
           ('to_be_sampled', 'to_be_preserved',
            'sample_due', 'sample_received', 'attachment_due',):
            can_attach = False
        if a_state in \
           ('to_be_sampled', 'to_be_preserved',
            'sample_due', 'sample_received',
            'attachment_due', 'to_be_verified',):
            can_verify = False
        if a_state in \
           ('to_be_sampled', 'to_be_preserved',
            'sample_due', 'sample_received',
            'attachment_due', 'to_be_verified', 'verified',):
            can_publish = False

    # Note: AR adds itself to the skiplist so we have to take it off again
    #       to allow multiple promotions (maybe by more than one deleted instance).
    if can_submit and workflow.getInfoFor(ar, 'review_state') == 'sample_received':
        try:
            workflow.doActionFor(ar, 'submit')
        except WorkflowException:
            pass
        skip(ar, 'submit', unskip=True)
    if can_attach and workflow.getInfoFor(ar, 'review_state') == 'attachment_due':
        try:
            workflow.doActionFor(ar, 'attach')
        except WorkflowException:
            pass
        skip(ar, 'attach', unskip=True)
    if can_verify and workflow.getInfoFor(ar, 'review_state') == 'to_be_verified':
        instance.REQUEST["workflow_skiplist"].append('verify all analyses')
        try:
            workflow.doActionFor(ar, 'verify')
        except WorkflowException:
            pass
        skip(ar, 'verify', unskip=True)
    if can_publish and workflow.getInfoFor(ar, 'review_state') == 'verified':
        instance.REQUEST["workflow_skiplist"].append('publish all analyses')
        try:
            workflow.doActionFor(ar, 'publish')
        except WorkflowException:
            pass
        skip(ar, 'publish', unskip=True)

    return
