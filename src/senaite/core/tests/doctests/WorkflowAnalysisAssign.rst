Analysis assign guard and event
-------------------------------

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowAnalysisAssign


Test Setup
..........

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.analysisrequest import create_partition
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from senaite.core.catalog import SAMPLE_CATALOG

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def new_ar(services):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': date_now,
    ...         'SampleType': sampletype.UID()}
    ...     service_uids = map(api.get_uid, services)
    ...     ar = create_analysisrequest(client, request, values, service_uids)
    ...     return ar

    >>> def try_transition(object, transition_id, target_state_id):
    ...      success = do_action_for(object, transition_id)[0]
    ...      state = api.get_workflow_status_of(object)
    ...      return success and state == target_state_id

    >>> def get_roles_for_permission(permission, context):
    ...     allowed = set(rolesForPermissionOn(permission, context))
    ...     return sorted(allowed)


Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = portal.bika_setup
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())


Assign transition and guard basic constraints
.............................................

Create an Analysis Request:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> transitioned = do_action_for(ar, "receive")

The status of the analyses is `unassigned`:

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> map(api.get_workflow_status_of, analyses)
    ['unassigned', 'unassigned', 'unassigned']

Create a Worksheet and add the analyses:

    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> for analysis in analyses:
    ...     worksheet.addAnalysis(analysis)
    >>> sorted((map(lambda an: an.getKeyword(), worksheet.getAnalyses())))
    ['Au', 'Cu', 'Fe']

Analyses have been transitioned to `assigned`:

    >>> map(api.get_workflow_status_of, analyses)
    ['assigned', 'assigned', 'assigned']

And all them are associated to the worksheet:

    >>> ws_uid = api.get_uid(worksheet)
    >>> filter(lambda an: an.getWorksheetUID() != ws_uid, analyses)
    []

Analyses do not have an Analyst assigned, though:

    >>> filter(lambda an: an.getAnalyst(), analyses)
    []

If I assign a user to the Worksheet, same user will be assigned to analyses:

    >>> worksheet.setAnalyst(TEST_USER_ID)
    >>> worksheet.getAnalyst() == TEST_USER_ID
    True

    >>> filter(lambda an: an.getAnalyst() != TEST_USER_ID, analyses)
    []

I can remove an analysis from the Worksheet:

    >>> cu = filter(lambda an: an.getKeyword() == "Cu", analyses)[0]
    >>> cu_uid = api.get_uid(cu)
    >>> worksheet.removeAnalysis(cu)
    >>> filter(lambda an: api.get_uid(an) == cu_uid, worksheet.getAnalyses())
    []

So the state of cu is now `unassigned`:

    >>> api.get_workflow_status_of(cu)
    'unassigned'

The Analyst is no longer assigned to the analysis:

    >>> cu.getAssignedAnalyst()
    ''

From `assigned` state I can do submit:

    >>> au = filter(lambda an: an.getKeyword() == "Au", analyses)[0]
    >>> api.get_workflow_status_of(au)
    'assigned'
    >>> au.setResult(20)
    >>> try_transition(au, "submit", "to_be_verified")
    True

And the analysis transitions to `to_be_verified`:

    >>> api.get_workflow_status_of(au)
    'to_be_verified'

While keeping the Analyst that was assigned to the worksheet:

    >>> au.getAnalyst() == TEST_USER_ID
    True

And since there is still one analysis in the Worksheet not yet submitted, the
Worksheet remains in `open` state:

    >>> api.get_workflow_status_of(worksheet)
    'open'

But if I remove the remaining analysis, the status of the Worksheet is promoted
to `to_be_verified`, cause all the analyses assigned are in this state:

    >>> fe = filter(lambda an: an.getKeyword() == "Fe", analyses)[0]
    >>> worksheet.removeAnalysis(fe)
    >>> fe.getWorksheet() is None
    True
    >>> api.get_workflow_status_of(fe)
    'unassigned'
    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'

In `to_be_verified` status, I cannot remove analyses:

    >>> worksheet.removeAnalysis(au)
    >>> map(lambda an: an.getKeyword(), worksheet.getAnalyses())
    ['Au']
    >>> au.getWorksheetUID() == api.get_uid(worksheet)
    True
    >>> api.get_workflow_status_of(au)
    'to_be_verified'

But I can still add more analyses:

    >>> worksheet.addAnalysis(fe)
    >>> filter(lambda an: an.getKeyword() == "Fe", worksheet.getAnalyses())
    [<Analysis at /plone/clients/client-1/W-0001/Fe>]

Causing the Worksheet to roll back to `open` status:

    >>> api.get_workflow_status_of(worksheet)
    'open'

If I remove `Fe` analysis again, worksheet is promoted to `to_be_verified`:

    >>> worksheet.removeAnalysis(fe)
    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'

Let's create another worksheet and add the remaining analyses:

    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> worksheet.addAnalysis(cu)
    >>> worksheet.addAnalysis(fe)
    >>> sorted((map(lambda an: an.getKeyword(), worksheet.getAnalyses())))
    ['Cu', 'Fe']

The status of the analyses is now `assigned`:

    >>> api.get_workflow_status_of(cu)
    'assigned'
    >>> api.get_workflow_status_of(fe)
    'assigned'

And I cannot re-assign:

    >>> isTransitionAllowed(cu, "assign")
    False

Submit results:

    >>> cu.setResult(12)
    >>> fe.setResult(12)
    >>> try_transition(cu, "submit", "to_be_verified")
    True
    >>> try_transition(fe, "submit", "to_be_verified")
    True

State of the analyses and worksheet is `to_be_verified`:

    >>> api.get_workflow_status_of(cu)
    'to_be_verified'
    >>> api.get_workflow_status_of(fe)
    'to_be_verified'
    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'


Assigned state of the sample
............................

The sample is reindexed when its analyses are assigned to a worksheet, so the
`assigned_state` of its catalog record is up-to-date. Note the value relies on
the worksheet the analyses are assigned to, not on their status alone. Create a
sample with a single analysis, so no other analysis of the sample is assigned
to a worksheet already:

    >>> sample = new_ar([Cu])
    >>> transitioned = do_action_for(sample, "receive")
    >>> cu = sample.getAnalyses(full_objects=True)[0]

    >>> def get_assigned_state(sample):
    ...     query = {"UID": api.get_uid(sample)}
    ...     brain = api.search(query, SAMPLE_CATALOG)[0]
    ...     return brain.assigned_state

    >>> get_assigned_state(sample)
    'unassigned'

    >>> len(api.search({"assigned_state": "unassigned",
    ...                 "UID": api.get_uid(sample)}, SAMPLE_CATALOG))
    1

Add the analysis to a worksheet:

    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> worksheet.addAnalysis(cu)
    >>> api.get_workflow_status_of(cu)
    'assigned'

Both the index and the metadata of the sample are `assigned`:

    >>> get_assigned_state(sample)
    'assigned'

    >>> len(api.search({"assigned_state": "assigned",
    ...                 "UID": api.get_uid(sample)}, SAMPLE_CATALOG))
    1

The same applies when the analyses are added in bulk:

    >>> sample = new_ar([Cu])
    >>> transitioned = do_action_for(sample, "receive")
    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> worksheet.addAnalyses(sample.getAnalyses(full_objects=True))
    >>> get_assigned_state(sample)
    'assigned'

The same applies to the ancestors of the sample. Create a sample with a single
analysis and move the analysis to a partition:

    >>> sample = new_ar([Cu])
    >>> transitioned = do_action_for(sample, "receive")
    >>> cu = sample.getAnalyses(full_objects=True)[0]
    >>> partition = create_partition(sample, request, [cu])
    >>> api.get_review_status(partition)
    'sample_received'

    >>> cu = partition.getAnalyses(full_objects=True)[0]
    >>> api.get_parent(cu) == partition
    True

    >>> get_assigned_state(partition)
    'unassigned'

    >>> get_assigned_state(sample)
    'unassigned'

Add the analysis of the partition to a worksheet:

    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> worksheet.addAnalysis(cu)
    >>> api.get_workflow_status_of(cu)
    'assigned'

Both the partition and its root sample are `assigned`:

    >>> get_assigned_state(partition)
    'assigned'

    >>> get_assigned_state(sample)
    'assigned'

    >>> len(api.search({"assigned_state": "assigned",
    ...                 "UID": api.get_uid(sample)}, SAMPLE_CATALOG))
    1


Check permissions for Assign transition
.......................................

Create an Analysis Request:

    >>> ar = new_ar([Cu])

The status of the analysis is `registered`:

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> map(api.get_workflow_status_of, analyses)
    ['registered']

But `assign` is not allowed unless we receive the Analysis Request so the
analysis is automatically transitioned to `unassigned` state:

    >>> isTransitionAllowed(analysis, "assign")
    False
    >>> transitioned = do_action_for(ar, "receive")
    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> map(api.get_workflow_status_of, analyses)
    ['unassigned']

Exactly these roles can assign:

    >>> analysis = analyses[0]
    >>> get_roles_for_permission("senaite.core: Transition: Assign Analysis", analysis)
    ['Analyst', 'LabClerk', 'LabManager', 'Manager']

Current user can assign because has the `LabManager` role:

    >>> isTransitionAllowed(analysis, "assign")
    True

Users with roles `Analyst` or `LabClerk` can assign too:

    >>> setRoles(portal, TEST_USER_ID, ['Analyst',])
    >>> isTransitionAllowed(analysis, "assign")
    True
    >>> setRoles(portal, TEST_USER_ID, ['LabClerk',])
    >>> isTransitionAllowed(analysis, "assign")
    True

Although other roles cannot:

    >>> setRoles(portal, TEST_USER_ID, ['Authenticated', 'Owner'])
    >>> isTransitionAllowed(analysis, "assign")
    False

Reset settings:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
