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
from senaite.core import logger


def get_workflow(thing, default=_marker):
    """Returns the primary DCWorkflowDefinition object for the thing passed-in

    :param thing: A single catalog brain, content object, supermodel, workflow,
        workflow id or portal type
    :type thing: DCWorkflowDefinition/ATContentType/DexterityContentType/
        CatalogBrain/SuperModel/string
    :return: The primary workflow of the thing
    :rtype: Products.DCWorkflow.DCWorkflow.DCWorkflowDefinition
    """
    if isinstance(thing, DCWorkflowDefinition):
        return thing

    if api.is_string(thing):
        # Look-up the workflow by id
        wf_tool = api.get_tool("portal_workflow")
        workflow = wf_tool.getWorkflowById(thing)
        if workflow:
            return workflow

        # Look-up the workflow by portal type
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

    if api.is_object(thing):
        # Return the primary workflow of the object
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
        ...         # Overwrite permissions
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
        if not wf.states.get(state_id):
            wf.states.addState(state_id)

        # Update the state with the settings passed-in
        update_workflow_state(wf, state_id, **values)

    # Update transitions
    transitions = transitions or {}
    for transition_id, values in transitions.items():

        # Create the transition if it does not exist yet
        if not wf.transitions.get(transition_id):
            wf.transitions.addTransition(transition_id)

        # Update the transition with the settings passed-in
        update_workflow_transition(wf, transition_id, **values)


def update_workflow_state(workflow, state_id, transitions=None,
                          permissions=None, **kwargs):
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
        >>> mappings = {
        ...     permissions.TransitionCancelAnalysisRequest: (),
        ...     permissions.TransitionReinstateAnalysisRequest: (),
        ... }

        >>> optional = {
        ...     "title": "Stored",
        ...     "description": "Sample is stored",
        ...     # Copy permissions from sample_received first
        ...     "permissions_copy_from": "sample_received",
        ... }

        >>> update_workflow_state(SAMPLE_WORKFLOW, "stored",
        ...                       transitions=trans,
        ...                       permissions=mappings,
        ...                       **optional)

    :param workflow: Workflow object or workflow id
    :type workflow: DCWorkflowDefinition/string
    :param state_id: workflow state id
    :type state_id: string
    :param transitions: Tuple or list of ids from transitions to be considered
        as exit transitions of the state. If a tuple, existing transitions are
        replaced by the new ones. If a list, existing transitions are extended
        with the new ones.
    :type transitions: list[string]
    :param permissions: dict of {permission_id:roles} where 'roles' can be a
        tuple or a list. If a tuple, existing roles are replaced by new ones
        and acquired is set to 'False'. If a list, existing roles are extended
        with the new ones and acquired is not changed.
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
    wf = get_workflow(workflow)
    state = wf.states.get(state_id)

    # Set basic info (title, description, etc.)
    state.title = kwargs.get("title", state.title)
    state.description = kwargs.get("description", state.description)

    # Check if we need to replace or extend existing transitions
    transitions = transitions or []
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
    permissions = permissions or {}
    update_workflow_permissions(wf, state_id, permissions)


def update_workflow_permissions(workflow, state_id, permissions):
    """Updates the permission mappings of an existing workflow state

    'permissions' is a dict of {permission_id: roles}, where roles can be a
    tuple or a list. Same principles from DCWorkflow apply:

    - if a tuple, existing roles are replaced and acquired is set 0
    - if a list, existing roles are extended and acquired is kept

    Usage::

        >>> from senaite.core import permissions
        >>> from senaite.core.workflow import SAMPLE_WORKFLOW

        >>> # Use tuples to override existing roles per permission and to also
        >>> # set acquire to False. To extend existing roles and preserve
        >>> # acquire, use a list
        >>> mappings = {
        ...     permissions.TransitionCancelAnalysisRequest: (),
        ...     permissions.TransitionReinstateAnalysisRequest: (),
        ... }

        >>> update_workflow_permissions(SAMPLE_WORKFLOW, "stored", mappings)

    :param workflow: Workflow object or workflow id
    :type workflow: DCWorkflowDefinition/string
    :param state_id: workflow state id
    :type state_id: string
    :param permissions: dict of {permission_id:roles} where 'roles' can be a
        tuple or a list. If a tuple, existing roles are replaced by new ones
        and acquired is set to 'False'. If a list, existing roles are extended
        with the new ones and acquired is not changed.
    :type: permissions: dict({string:tuple|list})
    """
    wf = get_workflow(workflow)
    state = wf.states.get(state_id)

    # Update permissions
    permissions = permissions or {}
    for perm_id, roles in permissions.items():

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

    :param workflow: Workflow object or workflow id
    :type workflow: DCWorkflowDefinition/string
    :param source_id: id of the workflow state to use as the source
    :type source_id: string
    :param destination_id: id of the workflow state to use as destination
    :type destination_id: string
    """
    wf = get_workflow(workflow)
    source = wf.states.get(source_id)

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
    """Updates an existing workflow transition

    Usage::

        >>> from senaite.core.workflow import SAMPLE_WORKFLOW

        >>> guard = {
        ...     "guard_permissions": "",
        ...     "guard_roles": "",
        ...     "guard_expr": "python:here.guard_handler('store')",
        ... }

        >>> update_workflow_transition(SAMPLE_WORKFLOW, "store",
        ...                            title="Store",
        ...                            action="Store sample",
        ...                            new_state="stored",
        ...                            guard=guard)

    :param workflow: Workflow object or workflow id
    :type workflow: DCWorkflowDefinition/string
    :param transition_id: the id of the transition to update
    :type transition_id: string
    :param title: (optional) the title of the workflow or None
    :type title: string
    :param new_state: (optional) the state that will reach the object after
        this transition is triggered.
    :type new_state: string
    :param after_script: (optional) the Script Python to execute after this
        transition is triggered.
    :type after_script: string
    :param action: (optional) the action name to display in the actions box
    :type action: string
    :param action_url: (optional) the url to use for this action
    :type action_url: string
    :param guard: (optional) a dict with the Guard properties
    :type guard: dict
    """
    wf = get_workflow(workflow)
    transition = wf.transitions.get(transition_id)

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
