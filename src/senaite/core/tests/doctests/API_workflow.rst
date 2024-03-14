API Workflow
------------

The workflow API provides a simple interface to manage workflows

Running this test from the buildout directory::

    bin/test test_textual_doctests -t API_workflow


Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from senaite.core.api import workflow as wapi
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
