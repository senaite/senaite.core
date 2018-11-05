# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFCore.utils import getToolByName
from bika.lims import api
from bika.lims.permissions import Unassign
from bika.lims.workflow import isBasicTransitionAllowed, isTransitionAllowed
from bika.lims.workflow import wasTransitionPerformed


def sample(obj):
    """ Returns true if the sample transition can be performed for the sample
    passed in.
    :returns: true or false
    """
    return isBasicTransitionAllowed(obj)

def retract(obj):
    """ Returns true if the sample transition can be performed for the sample
    passed in.
    :returns: true or false
    """
    return isBasicTransitionAllowed(obj)


def receive(obj):
    return isBasicTransitionAllowed(obj)


def publish(obj):
    """ Returns true if the 'publish' transition can be performed to the
    analysis passed in.
    In accordance with bika_analysis_workflow, 'publish'
    transition can only be performed if the state of the analysis is verified,
    so this guard only checks if the analysis state is active: there is no need
    of additional checks, cause the DC Workflow machinery will already take
    care of them.
    :returns: true or false
    """
    return isBasicTransitionAllowed(obj)


def import_transition(obj):
    return isBasicTransitionAllowed(obj)


def attach(obj):
    if not isBasicTransitionAllowed(obj):
        return False
    if not obj.getAttachment():
        return obj.getAttachmentOption() != 'r'
    return True


def assign(obj):
    return isBasicTransitionAllowed(obj)


def unassign(obj):
    """Check permission against parent worksheet
    """
    mtool = getToolByName(obj, "portal_membership")
    if not isBasicTransitionAllowed(obj):
        return False
    ws = obj.getBackReferences("WorksheetAnalysis")
    if not ws:
        return False
    ws = ws[0]
    if isBasicTransitionAllowed(ws):
        if mtool.checkPermission(Unassign, ws):
            return True
    return False


def guard_submit(analysis):
    """Return whether the transition "submit" can be performed or not
    """
    # Cannot submit if the analysis is cancelled
    if not api.is_active(analysis):
        return False

    # Cannot submit without a result
    if not analysis.getResult():
        return False

    # Check interims
    for interim in analysis.getInterimFields():
        if not interim.get("value", ""):
            return False

    # Check dependencies (analyses this analysis depends on)
    for dependency in analysis.getDependencies():
        if not isTransitionAllowed(dependency, "submit"):
            if not wasTransitionPerformed(dependency, "submit"):
                return False

    return True


def guard_verify(analysis):
    """Return whether the transition "verify" can be performed or not
    """
    # Cannot verify if the analysis is cancelled
    if not api.is_active(analysis):
        return False

    # Check dependencies (analyses this analysis depends on)
    for dependency in analysis.getDependencies():
        if not isTransitionAllowed(dependency, "verify"):
            if not wasTransitionPerformed(dependency, "verify"):
                return False

    # Check if the user that submitted the result is the current user
    m_tool = getToolByName(analysis, 'portal_membership')
    return analysis.isUserAllowedToVerify(m_tool.getAuthenticatedMember())
