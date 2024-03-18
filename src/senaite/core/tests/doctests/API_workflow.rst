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
    >>> from senaite.core.permissions import TransitionCancelAnalysisRequest
    >>> from senaite.core.permissions import TransitionReinstateAnalysisRequest
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

Get the workflow from a transition:

    >>> transition = workflow.transitions.get("receive")
    >>> wapi.get_workflow(transition)
    <DCWorkflowDefinition at /plone/portal_workflow/senaite_sample_workflow>

Get the workflow from a state:

    >>> state = workflow.states.get("sample_received")
    >>> wapi.get_workflow(state)
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


Get a workflow state
....................

We can get a workflow state by id:

    >>> wapi.get_state(workflow, "sample_received")
    <StateDefinition at /plone/portal_workflow/senaite_sample_workflow/states/sample_received>

And it works when using anything that can be resolved to a Workflow:

    >>> wapi.get_state(SAMPLE_WORKFLOW, "sample_received")
    <StateDefinition at /plone/portal_workflow/senaite_sample_workflow/states/sample_received>

    >>> wapi.get_state("AnalysisRequest", "sample_received")
    <StateDefinition at /plone/portal_workflow/senaite_sample_workflow/states/sample_received>

Rises an error if no workflow can be resolved though:

    >>> wapi.get_state("yummy", "sample_received")
    Traceback (most recent call last):
    [...]
    ValueError: Workflow not found: 'yummy'

Same if the workflow can be resolved, but the status doesn't:

    >>> wapi.get_state(workflow, "ghost")
    Traceback (most recent call last):
    [...]
    ValueError: State ghost not found for senaite_sample_workflow

Still, we can use default:

    >>> wapi.get_state(workflow, "ghost", default=None) is None
    True

But only when the workflow can be resolved:

    >>> wapi.get_state("yummy", "ghost", default=None)
    Traceback (most recent call last):
    [...]
    ValueError: Workflow not found: 'yummy'


Get a workflow transition
.........................

We can get a workflow transition by id:

    >>> wapi.get_transition(workflow, "receive")
    <TransitionDefinition at /plone/portal_workflow/senaite_sample_workflow/transitions/receive>

And it works when using anything that can be resolved to a Workflow:

    >>> wapi.get_transition(SAMPLE_WORKFLOW, "receive")
    <TransitionDefinition at /plone/portal_workflow/senaite_sample_workflow/transitions/receive>

    >>> wapi.get_transition("AnalysisRequest", "receive")
    <TransitionDefinition at /plone/portal_workflow/senaite_sample_workflow/transitions/receive>

Rises an error if no workflow can be resolved though:

    >>> wapi.get_transition("yummy", "receive")
    Traceback (most recent call last):
    [...]
    ValueError: Workflow not found: 'yummy'

Same if the workflow can be resolved, but the transition doesn't:

    >>> wapi.get_transition(workflow, "ghostify")
    Traceback (most recent call last):
    [...]
    ValueError: Transition ghostify not found for senaite_sample_workflow

Still, we can use default:

    >>> wapi.get_transition(workflow, "ghostify", default=None) is None
    True

But only when the workflow can be resolved:

    >>> wapi.get_transition("yummy", "ghostify", default=None)
    Traceback (most recent call last):
    [...]
    ValueError: Workflow not found: 'yummy'


Update permissions of a workflow state
......................................

We can add a non-managed permission in a workflow state easily:

    >>> wf = wapi.get_workflow(BATCH_WORKFLOW)
    >>> AddBatch in wf.permissions
    False

    >>> state = wapi.get_state(wf, "open")
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
    {'acquired': 1, 'roles': ['Analyst', 'Sampler', 'Verifier']}

But if we use a tuple, the system follows the same principles from DCWorkflow,
so roles are overwritten and acquired is set to False (`0`):

    >>> wapi.update_permission(state, AddBatch, ("Verifier", "LabManager"))
    >>> state.getPermissionInfo(AddBatch)
    {'acquired': 0, 'roles': ['LabManager', 'Verifier']}

And we can keep adding more roles:

    >>> wapi.update_permission(state, AddBatch, ["Analyst"])
    >>> state.getPermissionInfo(AddBatch)
    {'acquired': 0, 'roles': ['Analyst', 'LabManager', 'Verifier']}


Copy permissions from one state to another
..........................................

We can copy permissions across statuses easily:

    >>> source = wapi.get_state(BATCH_WORKFLOW, "open")
    >>> source.getPermissionInfo(AddBatch)
    {'acquired': 0, 'roles': ['Analyst', 'LabManager', 'Verifier']}

    >>> source.getPermissionInfo(DeleteObjects)
    {'acquired': 1, 'roles': []}

    >>> destination = wf.states.get("closed")
    >>> destination.getPermissionInfo(AddBatch)
    {'acquired': 1, 'roles': []}

    >>> destination.getPermissionInfo(DeleteObjects)
    {'acquired': 0, 'roles': []}

    >>> wapi.copy_permissions(source, destination)
    >>> destination.getPermissionInfo(AddBatch)
    {'acquired': 0, 'roles': ['Analyst', 'LabManager', 'Verifier']}

    >>> destination.getPermissionInfo(DeleteObjects)
    {'acquired': 1, 'roles': []}

    >>> source.getPermissionInfo(AddBatch)
    {'acquired': 0, 'roles': ['Analyst', 'LabManager', 'Verifier']}

    >>> source.getPermissionInfo(DeleteObjects)
    {'acquired': 1, 'roles': []}


Update a transition
...................

We can update a transition easily:

    >>> transition = wapi.get_transition(BATCH_WORKFLOW, "cancel")
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


Update a state
..............

We can update a state easily:

    >>> state = wapi.get_state(BATCH_WORKFLOW, "cancelled")
    >>> wapi.update_state(state, title='Ghosted', description='Ghost busters')
    >>> state.title
    'Ghosted'

    >>> state.description
    'Ghost busters'

Even reset the transitions using an empty tuple:

    >>> state.transitions
    ('reinstate',)

    >>> wapi.update_state(state, transitions=())
    >>> state.transitions
    ()

Add them by using a list:

    >>> wapi.update_state(state, transitions=["close", "reinstate"])
    >>> state.transitions
    ('close', 'reinstate')

    >>> wapi.update_state(state, transitions=["cancel"])
    >>> state.transitions
    ('cancel', 'close', 'reinstate')

Or replace them by using a tuple:

    >>> wapi.update_state(state, transitions=("cancel", "close"))
    >>> state.transitions
    ('cancel', 'close')

We can also tell the system to copy the permissions from another state:

    >>> wapi.update_state(state, permissions_copy_from="open")
    >>> state.getPermissionInfo(AddBatch)
    {'acquired': 0, 'roles': ['Analyst', 'LabManager', 'Verifier']}

    >>> state.getPermissionInfo(DeleteObjects)
    {'acquired': 1, 'roles': []}

Likewise, we can update the permissions with granted roles using a dictionary
with the permission id as keys and granted roles as values:

    >>> perms = {
    ...     AddBatch: ("LabManager", ),
    ...     DeleteObjects: ("Analyst", "LabClerk")
    ... }

    >>> wapi.update_state(state, permissions=perms)
    >>> state.getPermissionInfo(AddBatch)
    {'acquired': 0, 'roles': ['LabManager']}

    >>> state.getPermissionInfo(DeleteObjects)
    {'acquired': 0, 'roles': ['Analyst', 'LabClerk']}

And everything all-at-once:

    >>> perms = {
    ...     AddBatch: ("Analyst", "LabClerk"),
    ...     DeleteObjects: ["LabClerk"],
    ... }
    >>> wapi.update_state(state,
    ...                   title='Busty',
    ...                   description='Ghosting busters',
    ...                   transitions=('reinstate', 'close'),
    ...                   permissions_copy_from="open",
    ...                   permissions=perms)
    >>> state.title
    'Busty'
    >>> state.description
    'Ghosting busters'
    >>> state.transitions
    ('reinstate', 'close')
    >>> state.getPermissionInfo(AddBatch)
    {'acquired': 0, 'roles': ['Analyst', 'LabClerk']}
    >>> state.getPermissionInfo(DeleteObjects)
    {'acquired': 1, 'roles': ['LabClerk']}


Update a workflow all-at-once
.............................

It is possible to update a workflow all-at-once, with the creation of new
states and transitions included:

    >>> states = {
    ...     "stored": {
    ...         "title": "Stored",
    ...         "description": "Sample is stored",
    ...         "transitions": ("recover", "detach", "dispatch", ),
    ...         "permissions_copy_from": "sample_received",
    ...         "permissions": {
    ...             TransitionCancelAnalysisRequest: (),
    ...             TransitionReinstateAnalysisRequest: (),
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
    >>> wapi.update_workflow(SAMPLE_WORKFLOW, states=states, transitions=trans)
    >>> wf = wapi.get_workflow(SAMPLE_WORKFLOW)
    >>> sorted(wf.transitions.keys())
    [... 'store', 'submit', 'to_be_preserved', 'to_be_sampled', 'verify']

    >>> sorted(wf.states.keys())
    [... 'stored', 'to_be_preserved', 'to_be_sampled', 'to_be_verified', 'verified']

    >>> state = wapi.get_state(wf, "stored")
    >>> state.title
    'Stored'

    >>> state.transitions
    ('recover', 'detach', 'dispatch')

    >>> state.getPermissionInfo(TransitionCancelAnalysisRequest)
    {'acquired': 0, 'roles': []}
