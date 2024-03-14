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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.Guard import Guard
from senaite.core import logger

ANALYSIS_WORKFLOW = "senaite_analysis_workflow"
DUPLICATE_ANALYSIS_WORKFLOW = "senaite_duplicateanalysis_workflow"
REFERENCE_ANALYSIS_WORKFLOW = "senaite_referenceanalysis_workflow"
REFERENCE_SAMPLE_WORKFLOW = "senaite_referencesample_workflow"
REJECT_ANALYSIS_WORKFLOW = "senaite_rejectanalysis_workflow"
SAMPLE_WORKFLOW = "senaite_sample_workflow"
WORKSHEET_WORKFLOW = "senaite_worksheet_workflow"

_marker = object()


def get_workflow(thing, default=_marker):
    """Returns the primary DCWorkflowDefinition object for the thing passed-in

    :param thing: A single catalog brain, content object, supermodel, workflow,
        workflow id or portal type
    portal type
    :type thing: DCWorkflowDefinition, ATContentType, DexterityContentType,
        CatalogBrain or workflow id
    :returns: The primary workflow of the thing
    :rtype: DCWorkflowDefinition
    """
    if isinstance(thing, DCWorkflowDefinition):
        return thing

    if api.is_string(thing):
        # Look-up the workflow by id
        wf_tool = api.get_tool("portal_workflow")
        workflow = wf_tool.getWorkflowById(thing)
        # Might be the portal type instead
        workflow = workflow or wf_tool.getChainFor(thing)
        if workflow:
            return workflow
        if default is not _marker:
            return default
        raise ValueError("Workflow not found: %s " % repr(thing))

    if api.is_object(thing):
        # Return the primary workflow of the object
        workflows = api.get_workflows_for(thing)
        if len(workflows) == 1:
            return workflows[0]
        if default is not _marker:
            return default
        if len(workflows) > 1:
            raise ValueError("More than one workflow: %s" % repr(thing))
        raise ValueError("Workflow not found: %s" % repr(thing))

    if default is not _marker:
        return default

    raise ValueError("Type is not supported: %s" % repr(type(thing)))


def get_workflow_state(workflow_or_id, state_id, default=_marker):
    """Returns the workflow state with the given id
    """
    wf = get_workflow(workflow_or_id)
    state = wf.states.get(state_id)
    if not state:
        if default is _marker:
            raise ValueError("State %s not found for %s" % (state_id, wf.id))
        return default
    return state


def get_workflow_transition(workflow_or_id, transition_id, default=_marker):
    """Returns the workflow transition with the given id
    """
    wf = get_workflow(workflow_or_id)
    transition = wf.transitions.get(transition_id)
    if not transition:
        if default is _marker:
            raise ValueError("Transition %s not found for %s" %
                             (transition_id, wf.id))
        return default
    return transition


def update_workflow(workflow, **kwargs):
    """Updates the workflow with workflow_id with the settings passed-in
    """
    wf = get_workflow(workflow)

    # Set basic info (title, description, etc.)
    wf.title = kwargs.get("title", wf.title)
    wf.description = kwargs.get("description", wf.description)
    wf.initial_state = kwargs.get("initial_state", wf.initial_state)

    # Update states
    states = kwargs.get("states", {})
    for state_id, values in states.items():

        # Create the state if it does not exist yet
        if not wf.states.get(state_id):
            wf.states.addState(state_id)

        # Update the state with the settings passed-in
        update_workflow_state(wf, state_id, **values)

    # Update transitions
    transitions = kwargs.get("transitions", {})
    for transition_id, values in transitions.items():

        # Create the transition if it does not exist yet
        if not wf.transitions.get(transition_id):
            wf.transitions.addTransition(transition_id)

        # Update the transition with the settings passed-in
        update_workflow_transition(wf, transition_id, **values)


def update_workflow_state(workflow, state_id, **kwargs):
    """Updates the status of a workflow in accordance with settings passed-in

    Note that regarding the use of tuples and lists for permissions and
    transitions, the same principles from DCWorkflow apply. This is:

    - Transitions passed-in as a list are added to existing transitions
    - Transitions passed-in as a tuple replace the existing transitions
    """
    wf = get_workflow(workflow)
    state = get_workflow_state(wf, state_id)

    # Set basic info (title, description, etc.)
    state.title = kwargs.get("title", state.title)
    state.description = kwargs.get("description", state.description)

    # Check if we need to replace or extend existing transitions
    transitions = kwargs.get("transitions", []) or []
    if isinstance(transitions, list):
        transitions = set(transitions)
        transitions.update(state.transitions)
        transitions = tuple(transitions)

    # Set transitions
    state.transitions = transitions

    # Copy permissions fromm another state
    perms_source = kwargs.get("permissions_copy_from", False)
    if perms_source:
        copy_workflow_permissions(wf, perms_source, state_id)

    # Update existing permissions
    permissions = kwargs.get("permissions", {})
    update_workflow_permissions(wf, state_id, permissions)


def update_workflow_permissions(workflow, state_id, mappings):
    """Updates the permission mappings of a workflow status

    Mappings is a dict of {permission_id: roles}, where roles can be a tuple
    or a list.

    Same principles from DCWorkflow apply:
    - if a tuple, existing roles are replaced and acquired is set 0
    - if a list, existing roles are extended and acquired is kept
    """
    wf = get_workflow(workflow)
    state = get_workflow_state(wf, state_id)

    # Update permissions
    for perm_id, roles in mappings.items():

        # Resolve acquire
        if isinstance(roles, tuple):
            acquired = 0
        else:
            info = state.getPermissionInfo(perm_id) or {}
            acquired = info.get("acquired", 1)
            roles = set(roles)
            roles.update(info.get("roles", []))
            roles = tuple(roles)

        # Add this permission to the workflow if not globally defined yet
        if perm_id not in workflow.permissions:
            wf.permissions = wf.permissions + (perm_id,)

        # Set the permission
        logger.info("{}.{}: '{}' (acquired={}): '{}'".format(
            wf.id, state.id, perm_id, repr(acquired), ', '.join(roles)))
        state.setPermission(perm_id, acquired, roles)


def copy_workflow_permissions(workflow, source_id, destination_id):
    """Copies the permissions from the source status to destination status
    """
    wf = get_workflow(workflow)
    source = get_workflow_state(wf, source_id)

    # Create the mapping of permissions -> roles
    mapping = {}
    for perm_id in source.permissions:
        perm_info = source.getPermissionInfo(perm_id)
        acquired = perm_info.get("acquired", 1)
        roles = perm_info.get("roles", acquired and [] or ())
        mapping[perm_id] = roles

    # Update the permissions at destination
    update_workflow_permissions(wf, destination_id, mapping)


def update_workflow_transition(workflow, transition_id, **kwargs):
    """Updates the workflow transition in accordance with settings passed-in
    """
    wf = get_workflow(workflow)
    transition = get_workflow_transition(wf, transition_id)

    # Update transition properties
    title = kwargs.get("title", transition.title)

    new_state_id = kwargs.get("new_state", transition.new_state_id)
    if new_state_id in ["None", None]:
        new_state_id = ""

    after_script = kwargs.get("after_script", transition.after_script_name)
    if after_script in ["None", None]:
        after_script = ""

    transition.setProperties(
        title=title,
        new_state_id=new_state_id,
        after_script_name=after_script,
        actbox_name=kwargs.get("action", title),
        actbox_url=kwargs.get("action_url", ""),
    )

    # Update transition guard
    guard = transition.guard or Guard()
    if "guard" in kwargs:
        guard.changeFromProperties(kwargs.get("guard"))
    transition.guard = guard
