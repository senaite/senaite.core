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
from bika.lims.api import _marker
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.Guard import Guard
from Products.DCWorkflow.States import StateDefinition
from Products.DCWorkflow.Transitions import TransitionDefinition
from senaite.core import logger


def get_workflow(thing, default=_marker):
    """Returns the primary DCWorkflowDefinition object for the thing passed-in

    :param thing: A single catalog brain, content object, supermodel, workflow,
        workflow id, workflow state, workflow transition or portal type
    :type thing: DCWorkflowDefinition/StateDefinition/TransitionDefinition/
        ATContentType/DexterityContentType/CatalogBrain/SuperModel/string
    :return: The primary workflow of the thing
    :rtype: Products.DCWorkflow.DCWorkflow.DCWorkflowDefinition
    """
    if isinstance(thing, DCWorkflowDefinition):
        return thing
    if isinstance(thing, StateDefinition):
        return thing.getWorkflow()
    if isinstance(thing, TransitionDefinition):
        return thing.getWorkflow()

    if api.is_string(thing):
        # Look-up the workflow by id
        wf_tool = api.get_tool("portal_workflow")
        workflow = wf_tool.getWorkflowById(thing)
        if workflow:
            return workflow

    if api.is_string(thing) or api.is_object(thing):
        # Look-up the workflow by portal type or object
        wf_tool = api.get_tool("portal_workflow")
        workflows = wf_tool.getChainFor(thing)
        if len(workflows) == 1:
            return wf_tool.getWorkflowById(workflows[0])
        if default is not _marker:
            if default is None:
                return default
            return get_workflow(default)
        if len(workflows) > 1:
            raise ValueError("More than one workflow: %s" % repr(thing))
        raise ValueError("Workflow not found: %s" % repr(thing))

    if default is not _marker:
        if default is None:
            return default
        return get_workflow(default)

    raise ValueError("Type is not supported: %s" % repr(type(thing)))


def get_state(workflow, state_id, default=_marker):
    """Returns the workflow state with the given id
    :param workflow: Workflow object or workflow id
    :type workflow: DCWorkflowDefinition/string
    :param state_id: Workflow state id
    :type state_id: string
    :return: The state object for the given workflow and id
    :rtype: Products.DCWorkflow.States.StateDefinition
    """
    wf = get_workflow(workflow)
    state = wf.states.get(state_id)
    if state:
        return state
    if default is not _marker:
        return default
    raise ValueError("State %s not found for %s" % (state_id, wf.id))


def get_transition(workflow, transition_id, default=_marker):
    """Returns the workflow transition with the given id
    :param workflow: Workflow object or workflow id
    :type workflow: DCWorkflowDefinition/string
    :param transition_id: Workflow transition id
    :type transition_id: string
    :return: The transition object for the given workflow and id
    :rtype: Products.DCWorkflow.Transitions.TransitionDefinition
    """
    wf = get_workflow(workflow)
    transition = wf.transitions.get(transition_id)
    if transition:
        return transition
    if default is not _marker:
        return default
    raise ValueError("Transition %s not found for %s" % (transition_id, wf.id))


def update_workflow(workflow, states=None, transitions=None, **kwargs):
    """Updates an existing workflow

    Usage::

        >>> from senaite.core import permissions
        >>> from senaite.core.workflow import SAMPLE_WORKFLOW
        >>> states = {
        ...     "stored": {
        ...         "title": "Stored",
        ...         "description": "Sample is stored",
        ...         # Use tuples to overwrite existing transitions. To extend
        ...         # existing transitions, use a list
        ...         "transitions": ("recover", "detach", "dispatch", ),
        ...         # Copy permissions from sample_received first
        ...         "permissions_copy_from": "sample_received",
        ...         # Permissions mapping
        ...         "permissions": {
        ...             # Use tuples to overwrite existing and acquire=False.
        ...             # To extend existing roles, use a list
        ...             permissions.TransitionCancelAnalysisRequest: (),
        ...             permissions.TransitionReinstateAnalysisRequest: (),
        ...         }
        ...     },
        ... }
        >>> trans = {
        ...     "store": {
        ...         "title": "Store",
        ...         "new_state": "stored",
        ...         "action": "Store sample",
        ...         "guard": {
        ...             "guard_permissions": "",
        ...             "guard_roles": "",
        ...             "guard_expr": "python:here.guard_handler('store')",
        ...         }
        ...     },
        ... }
        >>> update_workflow(SAMPLE_WORKFLOW, states=states, transitions=trans)

    :param workflow: Workflow object or workflow id
    :type workflow: DCWorkflowDefinition/string
    :param states: states to be updated/created
    :type states: dict of {state_id:{<state_properties>}}
    :param transitions: transitions to be updated/created
    :type transitions: dict of {transition_id:<transition_properties>}
    :param title: (optional) the title of the workflow or None
    :type title: string
    :param description: (optional) the description of the workflow or None
    :type description: string
    :param initial_state: (optional) the initial status id of the workflow
    :type initial_state: string
    """
    wf = get_workflow(workflow)

    # Set basic info (title, description, etc.)
    wf.title = kwargs.get("title", wf.title)
    wf.description = kwargs.get("description", wf.description)
    wf.initial_state = kwargs.get("initial_state", wf.initial_state)

    # Update states
    states = states or {}
    for state_id, values in states.items():

        # Create the state if it does not exist yet
        state = wf.states.get(state_id)
        if not state:
            wf.states.addState(state_id)
            state = wf.states.get(state_id)

        # Update the state with the settings passed-in
        update_state(state, **values)

    # Update transitions
    transitions = transitions or {}
    for transition_id, values in transitions.items():

        transition = wf.transitions.get(transition_id)
        if not transition:
            wf.transitions.addTransition(transition_id)
            transition = wf.transitions.get(transition_id)

        # Update the transition with the settings passed-in
        update_transition(transition, **values)


def update_state(state, transitions=None, permissions=None, **kwargs):
    """Updates the state of an existing workflow

    Note that regarding the use of tuples/lists for roles in permissions and
    in transitions, the same principles from DCWorkflow apply. This is:

    - Transitions passed-in as a list extend the existing ones
    - Transitions passed-in as a tuple replace the existing ones
    - Roles passed-in as a list extend the existing ones and acquire is kept
    - Roles passed-in as a tuple replace the existing ones and acquire is '0'

    Usage::

        >>> from senaite.core import permissions
        >>> from senaite.core.workflow import SAMPLE_WORKFLOW

        >>> # Use tuples to overwrite existing transitions. To extend
        >>> # existing transitions, use a list
        >>> trans = ("recover", "detach", "dispatch", )

        >>> # Use tuples to override existing roles per permission and to also
        >>> # set acquire to False. To extend existing roles and preserve
        >>> # acquire, use a list
        >>> perms = {
        ...     permissions.TransitionCancelAnalysisRequest: (),
        ...     permissions.TransitionReinstateAnalysisRequest: (),
        ... }

        >>> kwargs = {
        ...     "title": "Stored",
        ...     "description": "Sample is stored",
        ...     # Copy permissions from sample_received first
        ...     "permissions_copy_from": "sample_received",
        ... }

        >>> state = get_state(SAMPLE_WORKFLOW, "stored")
        >>> update_state(state, transitions=trans, permissions=perms, **kwargs)

    :param state: Workflow state definition object
    :type state: Products.DCWorkflow.States.StateDefinition
    :param transitions: Tuple or list of ids from transitions to be considered
        as exit transitions of the state. If a tuple, existing transitions are
        replaced by the new ones. If a list, existing transitions are extended
        with the new ones. If None, keeps the original transitions.
    :type transitions: list[string]
    :param permissions: dict of {permission_id:roles} where 'roles' can be a
        tuple or a list. If a tuple, existing roles are replaced by new ones
        and acquired is set to 'False'. If a list, existing roles are extended
        with the new ones and acquired is not changed. If None, keeps the
        original permissions
    :type: permissions: dict({string:tuple|list})
    :param title: (optional) the title of the workflow or None
    :type title: string
    :param description: (optional) the description of the workflow or None
    :type description: string
    :param permissions_copy_from: (optional) the id of the status to copy the
        permissions from to the given status. When set, the permissions from
        the source status are copied to the given status before the update of
        the permissions with those passed-in takes place.
    :type: permissions_copy_from: string
    """
    # set basic info (title, description, etc.)
    state.title = kwargs.get("title", state.title)
    state.description = kwargs.get("description", state.description)

    # check if we need to replace or extend existing transitions
    if transitions is None:
        transitions = state.transitions
    elif isinstance(transitions, list):
        transitions = set(transitions)
        transitions.update(state.transitions)
        transitions = tuple(transitions)

    # set transitions
    state.transitions = transitions

    # copy permissions fromm another state
    source = kwargs.get("permissions_copy_from")
    if source:
        wf = get_workflow(state)
        source = wf.states.get(source)
        copy_permissions(source, state)

    # update existing permissions
    permissions = permissions or {}
    for perm_id, roles in permissions.items():
        update_permission(state, perm_id, roles)


def update_transition(transition, **kwargs):
    """Updates a workflow transition

    Usage::

        >>> from senaite.core.workflow import SAMPLE_WORKFLOW

        >>> guard = {
        ...     "guard_permissions": "",
        ...     "guard_roles": "",
        ...     "guard_expr": "python:here.guard_handler('store')",
        ... }

        >>> wf = get_workflow(SAMPLE_WORKFLOW)
        >>> transition = wf.transitions.get("store")
        >>> update_transition(transition,
        ...                   title="Store",
        ...                   description="The action to store the sample",
        ...                   action="Store sample",
        ...                   new_state="stored",
        ...                   guard=guard)

    :param transition: Workflow transition definition object
    :type transition: Products.DCWorkflow.Transitions.TransitionDefinition
    :param title: (optional) the title of the transition
    :type title: string
    :param description: (optional) the descrioption of the transition
    :type title: string
    :param new_state: (optional) the state of the object after the transition
    :type new_state: string
    :param after_script: (optional) Script (Python) to run after the transition
    :type after_script: string
    :param action: (optional) the action name to display in the actions box
    :type action: string
    :param action_url: (optional) the url to use for this action. The
        %(content_url) wildcard is replaced by absolute path at runtime. If
        empty, the default `content_status_modify?workflow_action=<action_id>`
        will be used at runtime
    :type action_url: string
    :param guard: (optional) a dict with Guard properties. The supported
        properties are: 'guard_roles', 'guard_groups', 'guard_expr' and
        'guard_permissions'
    :type guard: dict
    """
    # attrs conversions
    mapping = {
        "title": "title",
        "description": "description",
        "action": "actbox_name",
        "action_url": "actbox_url",
        "after_script": "after_script_name",
        "new_state": "new_state_id",
    }
    properties = {}
    for key, property_id in mapping.items():
        default = getattr(transition, property_id) or ""
        value = kwargs.get(key, None)
        if value is None:
            value = default
        properties[property_id] = value

    # update the transition properties
    transition.setProperties(**properties)

    # update the guard
    guard = transition.guard or Guard()
    guard_props = kwargs.get("guard")
    if guard_props:
        guard.changeFromProperties(guard_props)
    transition.guard = guard


def update_permission(state, permission_id, roles):
    """Updates the permission mappings of an existing workflow state

    :param state: Workflow state definition object
    :type state: Products.DCWorkflow.States.StateDefinition
    :param permission_id: id of the permission
    :type permission_id: string
    :param roles: List or tuple with roles to which the given permission has
        to be granted for the workflow status. If a tuple, acquire is set to
        False and roles overwritten. Thus, an empty tuple clears all roles for
        this permission and state. If a list, the existing roles are extended
        with new ones and acquire setting is not modified.
    :type roles: list/tuple
    """
    # resolve acquire
    if isinstance(roles, tuple):
        acquired = 0
    else:
        info = state.getPermissionInfo(permission_id) or {}
        acquired = info.get("acquired", 1)
        roles = set(roles)
        roles.update(info.get("roles", []))

    # sort them for human-friendly reading on retrieval
    roles = tuple(sorted(roles))

    # add this permission to the workflow if not globally defined yet
    wf = get_workflow(state)
    if permission_id not in wf.permissions:
        wf.permissions = wf.permissions + (permission_id,)

    # set the permission
    logger.info("{}.{}: '{}' (acquired={}): '{}'".format(
        wf.id, state.id, permission_id, repr(acquired), ', '.join(roles)))
    state.setPermission(permission_id, acquired, roles)


def copy_permissions(source, destination):
    """Copies the permission mappings of a workflow state to another

    :param source: Workflow state definition object used as source
    :type source: Products.DCWorkflow.States.StateDefinition
    :param destination: Workflow state definition object used as destination
    :type destination: Products.DCWorkflow.States.StateDefinition
    """
    for permission in source.permissions:
        info = source.getPermissionInfo(permission)
        roles = info.get("roles") or []
        acquired = info.get("acquired", 1)
        # update the roles for this permission at destination
        destination.setPermission(permission, acquired, sorted(roles))


def is_transition_allowed(obj, transition_id):
    """Returns whether the transition with the given id can be performed
    against the object.

    :param obj: object to evaluate the transition against
    :type obj: ATContentType/DexterityContentType/CatalogBrain/UID
    :param transition_id: Workflow transition id
    :type transition_id: string
    :returns: True if the transition with the given id can be performed
    :rtype: bool
    """
    obj = api.get_object(obj)
    wf = get_workflow(obj)
    if wf.isActionSupported(obj, transition_id):
        return True
    return False
