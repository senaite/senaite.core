Sample dispatch workflow
------------------------

The `dispatch` transition is gated by a global `dispatch_workflow_enabled`
setup flag (disabled by default), mirroring the dispose workflow. When a
sample is dispatched, it is marked with the `IDispatched` interface and its
analyses are transitioned to the read-only `locked` state. Restoring the
sample removes the marker and brings the analyses back to their previous
status. Dispatch and restore propagate to the sample partitions as well.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowSampleDispatch

Test Setup
..........

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.api.security import check_permission
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.analysisrequest import create_partition
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from senaite.core.interfaces import IDispatched
    >>> from senaite.core.permissions import EditResults
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD

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

    >>> def new_sample(services, client, contact, sampletype):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': date_now,
    ...         'SampleType': sampletype.UID()}
    ...     service_uids = map(api.get_uid, services)
    ...     sample = create_analysisrequest(client, request, values, service_uids)
    ...     return sample

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = api.get_bika_setup()
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")

The dispatch workflow is optional, so we enable it first:

    >>> setup.setDispatchWorkflowEnabled(True)

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


Dispatch transition and guard basic constraints
...............................................

Create a new sample:

    >>> sample = new_sample([Cu, Fe, Au], client, contact, sampletype)
    >>> api.get_workflow_status_of(sample)
    'sample_due'

Because the sample is not yet received, it cannot be dispatched:

    >>> "restore" in getAllowedTransitions(sample)
    False

Receive the sample:

    >>> transitioned = do_action_for(sample, "receive")
    >>> api.get_workflow_status_of(sample)
    'sample_received'

The dispatch transition is gated by the setup flag. When disabled, it is
not offered; when enabled, it is:

    >>> setup.setDispatchWorkflowEnabled(False)
    >>> isTransitionAllowed(sample, "dispatch")
    False
    >>> setup.setDispatchWorkflowEnabled(True)
    >>> isTransitionAllowed(sample, "dispatch")
    True

Now the sample can be dispatched:

    >>> transitioned = do_action_for(sample, "dispatch")
    >>> api.get_workflow_status_of(sample)
    'dispatched'

The sample is marked as dispatched and its analyses are locked:

    >>> IDispatched.providedBy(sample)
    True

    >>> sorted(set(map(api.get_workflow_status_of,
    ...                 sample.getAnalyses(full_objects=True))))
    ['locked']

    >>> check_permission(EditResults, sample.getAnalyses(full_objects=True)[0])
    False

At this point, only "restore" transition is possible:

    >>> getAllowedTransitions(sample)
    ['restore']

When the sample is restored, the status becomes the previous before the dispatch
took place, the marker is removed and the analyses are unlocked:

    >>> transitioned = do_action_for(sample, "restore")
    >>> api.get_workflow_status_of(sample)
    'sample_received'

    >>> IDispatched.providedBy(sample)
    False

    >>> sorted(set(map(api.get_workflow_status_of,
    ...                 sample.getAnalyses(full_objects=True))))
    ['unassigned']

Dispatching can be done again now:

    >>> transitioned = do_action_for(sample, "dispatch")
    >>> api.get_workflow_status_of(sample)
    'dispatched'

And restoring as well:

    >>> transitioned = do_action_for(sample, "restore")
    >>> api.get_workflow_status_of(sample)
    'sample_received'

However, if the sample analyses are assinged, we prevent dispatching:

    >>> analyses = sample.getAnalyses(full_objects=True)
    >>> map(api.get_workflow_status_of, analyses)
    ['unassigned', 'unassigned', 'unassigned']
    >>> analysis = analyses[0]
    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> worksheet.addAnalysis(analysis)
    >>> api.get_workflow_status_of(analysis)
    'assigned'
    >>> isTransitionAllowed(sample, "dispatch")
    False

Unassign analysis from the worksheet again:

    >>> worksheet.removeAnalysis(analysis)
    >>> isTransitionAllowed(sample, "dispatch")
    True

Partitions can be dispatched as well:

    >>> partition1 = create_partition(sample, request, [analyses[0]])
    >>> api.get_workflow_status_of(partition1)
    'sample_received'
    >>> isTransitionAllowed(partition1, "dispatch")
    True

    >>> partition2 = create_partition(sample, request, [analyses[1]])
    >>> api.get_workflow_status_of(partition2)
    'sample_received'
    >>> isTransitionAllowed(partition2, "dispatch")
    True


Dispatching the first partition leaves the root sample and the other partition
unchanged:

    >>> transitioned = do_action_for(partition1, "dispatch")
    >>> api.get_workflow_status_of(partition1)
    'dispatched'

    >>> api.get_workflow_status_of(partition2)
    'sample_received'

    >>> api.get_workflow_status_of(sample)
    'sample_received'

But when both partitions are dispatched, the root sample will be set to
dispatched as well:

    >>> transitioned = do_action_for(partition2, "dispatch")
    >>> api.get_workflow_status_of(partition2)
    'dispatched'

    >>> api.get_workflow_status_of(partition1)
    'dispatched'

    >>> api.get_workflow_status_of(sample)
    'dispatched'


Restoring the root sample will restore all partitions as well:

    >>> transitioned = do_action_for(sample, "restore")
    >>> api.get_workflow_status_of(sample)
    'sample_received'

    >>> api.get_workflow_status_of(partition1)
    'sample_received'

    >>> api.get_workflow_status_of(partition2)
    'sample_received'

Dispatching the root sample will dispatch all partitions as well:

    >>> transitioned = do_action_for(sample, "dispatch")
    >>> api.get_workflow_status_of(sample)
    'dispatched'

    >>> api.get_workflow_status_of(partition1)
    'dispatched'

    >>> api.get_workflow_status_of(partition2)
    'dispatched'
