API Workflow
------------

The workflow API provides a simple interface to manage workflows

Running this test from the buildout directory::

    bin/test test_textual_doctests -t API_workflow


Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from Products.CMFCore.permissions import DeleteObjects
    >>> from senaite.core.api import workflow as wapi
    >>> from senaite.core.permissions import AddBatch
    >>> from senaite.core.permissions import TransitionClose
    >>> from senaite.core.workflow import BATCH_WORKFLOW
    >>> from senaite.core.workflow import SAMPLE_WORKFLOW

Get a workflow
..............

Get a workflow by id:

    >>> wapi.get_workflow(SAMPLE_WORKFLOW)
    <DCWorkflowDefinition at /plone/portal_workflow/senaite_sample_workflow>

Get the primary workflow of a portal type:

    >>> wapi.get_workflow("AnalysisRequest")
    <DCWorkflowDefinition at /plone/portal_workflow/senaite_sample_workflow>

    >>> wapi.get_workflow("Client")
    <DCWorkflowDefinition at /plone/portal_workflow/senaite_client_workflow>

Get the primary workflow of an object-like content:

    >>> portal = api.get_portal()
    >>> clients = portal.clients
    >>> wapi.get_workflow(clients)
    <DCWorkflowDefinition at /plone/portal_workflow/senaite_clients_workflow>

Get the workflow by workflow:

    >>> workflow = wapi.get_workflow(SAMPLE_WORKFLOW)
    >>> wapi.get_workflow(workflow)
    <DCWorkflowDefinition at /plone/portal_workflow/senaite_sample_workflow>

An error arises if the parameter is not valid:

    >>> wapi.get_workflow("no_workflow")
    Traceback (most recent call last):
    [...]
    ValueError: Workflow not found: 'no_workflow'

    >>> wapi.get_workflow(object())
    Traceback (most recent call last):
    [...]
    ValueError: Type is not supported: <type 'object'>

    >>> wapi.get_workflow(None)
    Traceback (most recent call last):
    [...]
    ValueError: Type is not supported: <type 'NoneType'>

    >>> wapi.get_workflow("")
    Traceback (most recent call last):
    [...]
    ValueError: Workflow not found: ''

Still, we can use `default`:

    >>> wapi.get_workflow("no_workflow", default=None) is None
    True

But unless `None`, `default` has to be a workflow as well:

    >>> wapi.get_workflow("no_workflow", default=SAMPLE_WORKFLOW)
    <DCWorkflowDefinition at /plone/portal_workflow/senaite_sample_workflow>

    >>> wapi.get_workflow("no_workflow", default=object())
    Traceback (most recent call last):
    [...]
    ValueError: Type is not supported: <type 'object'>


Update permissions of a workflow state
......................................

We can add a non-managed permission in a workflow state easily:

    >>> wf = wapi.get_workflow(BATCH_WORKFLOW)
    >>> AddBatch in wf.permissions
    False

    >>> state = wf.states.get("open")
    >>> state.getPermissionInfo(AddBatch)
    {'acquired': 1, 'roles': []}

    >>> wapi.update_permission(state, AddBatch, ["Analyst", ])
    >>> state.getPermissionInfo(AddBatch)
    {'acquired': 1, 'roles': ['Analyst']}

And the permission is also present now as a workflow's managed permission:

    >>> AddBatch in wf.permissions
    True

Note that if we use a list of roles, the system keeps acquired setting and
extends the existing roles with the new ones:

    >>> wapi.update_permission(state, AddBatch, ["Sampler", "Verifier"])
    >>> state.getPermissionInfo(AddBatch)
    {'acquired': 1, 'roles': ['Verifier', 'Analyst', 'Sampler']}

But if we use a tuple, the system follows the same principles from DCWorkflow,
so roles are overwritten and acquired is set to False (`0`):

    >>> wapi.update_permission(state, AddBatch, ("Verifier", "LabManager"))
    >>> state.getPermissionInfo(AddBatch)
    {'acquired': 0, 'roles': ['Verifier', 'LabManager']}

And we can keep adding more roles:

    >>> wapi.update_permission(state, AddBatch, ["Analyst"])
    >>> state.getPermissionInfo(AddBatch)
    {'acquired': 0, 'roles': ['LabManager', 'Verifier', 'Analyst']}


Copy permissions from one state to another
..........................................

We can copy permissions across statuses easily:

    >>> wf = wapi.get_workflow(BATCH_WORKFLOW)
    >>> source = wf.states.get("open")
    >>> source.getPermissionInfo(AddBatch)
    {'acquired': 0, 'roles': ['LabManager', 'Verifier', 'Analyst']}

    >>> source.getPermissionInfo(DeleteObjects)
    {'acquired': 1, 'roles': []}

    >>> destination = wf.states.get("closed")
    >>> destination.getPermissionInfo(AddBatch)
    {'acquired': 1, 'roles': []}

    >>> destination.getPermissionInfo(DeleteObjects)
    {'acquired': 0, 'roles': []}

    >>> wapi.copy_permissions(source, destination)
    >>> destination.getPermissionInfo(AddBatch)
    {'acquired': 0, 'roles': ['LabManager', 'Verifier', 'Analyst']}

    >>> destination.getPermissionInfo(DeleteObjects)
    {'acquired': 1, 'roles': []}

    >>> source.getPermissionInfo(AddBatch)
    {'acquired': 0, 'roles': ['LabManager', 'Verifier', 'Analyst']}

    >>> source.getPermissionInfo(DeleteObjects)
    {'acquired': 1, 'roles': []}


Update a transition
...................

We can update a transition easily:

    >>> wf = wapi.get_workflow(BATCH_WORKFLOW)
    >>> transition = wf.transitions.get("cancel")
    >>> wapi.update_transition(transition, title='Discard')
    >>> transition.title
    'Discard'

    >>> wapi.update_transition(transition, new_state="closed", action="Discard")
    >>> transition.new_state_id
    'closed'

    >>> transition.actbox_name
    'Discard'

And everything all-at-once, guard included:

    >>> guard = {
    ...     "guard_permissions": TransitionClose,
    ...     "guard_expr": "python:here.guard_handler('close')",
    ...     "guard_roles": "Analyst;LabManager",
    ... }
    >>> wapi.update_transition(transition,
    ...                        title='My close was cancel transition',
    ...                        action='My close',
    ...                        new_state='closed',
    ...                        guard=guard)
    >>> transition.title
    'My close was cancel transition'
    >>> transition.actbox_name
    'My close'
    >>> transition.new_state_id
    'closed'
    >>> transition.guard.permissions
    ('senaite.core: Transition: Close',)
    >>> transition.guard.expr.text
    "python:here.guard_handler('close')"

