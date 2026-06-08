Sample reattach
---------------

The `reattach` workflow transition is the inverse of `detach`. It
re-links a previously detached partition back to its original primary
sample. The guard only allows the transition when the original primary
is still reachable and both samples share the same review state, so
re-merging cannot break the parent's state machine.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t SampleReattach


Test Setup
..........

Imports:

    >>> from DateTime import DateTime
    >>> from bika.lims import api
    >>> from bika.lims.interfaces import IAnalysisRequestPartition
    >>> from bika.lims.interfaces import IDetachedPartition
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.analysisrequest import create_partition
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import isTransitionAllowed

Functional helpers:

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

Variables:

    >>> date_now = timestamp()
    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bika_setup = portal.bika_setup
    >>> sampletypes = setup.sampletypes
    >>> analysiscategories = setup.analysiscategories
    >>> bika_analysisservices = bika_setup.bika_analysisservices

Test user — Lab Manager:

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager', 'LabManager'])


Setup Client, Contact, SampleType and AnalysisService
.....................................................

    >>> clients = self.portal.clients
    >>> client = api.create(clients, "Client", Name="ACME", ClientID="A")
    >>> contact = api.create(client, "Contact", Firstname="John", Surname="Doe")
    >>> sampletype = api.create(sampletypes, "SampleType",
    ...     Prefix="water", MinimumVolume="100 ml")
    >>> category = api.create(analysiscategories, "AnalysisCategory",
    ...     title="Water")
    >>> service = api.create(bika_analysisservices, "AnalysisService",
    ...     title="PH", ShortTitle="ph", Category=category, Keyword="PH")


Create the primary Sample and partition it
..........................................

    >>> values = {
    ...     "Client": client.UID(),
    ...     "Contact": contact.UID(),
    ...     "SamplingDate": date_now,
    ...     "DateSampled": date_now,
    ...     "SampleType": sampletype.UID(),
    ... }
    >>> primary = create_analysisrequest(client, request, values,
    ...                                  [service.UID()])
    >>> _ = do_action_for(primary, "receive")
    >>> api.get_workflow_status_of(primary)
    'sample_received'

Create a partition off the primary:

    >>> partition = create_partition(primary, request, primary.getAnalyses())
    >>> IAnalysisRequestPartition.providedBy(partition)
    True
    >>> partition.getParentAnalysisRequest() == primary
    True


Detach the partition
....................

    >>> success, message = do_action_for(partition, "detach")
    >>> success
    True

After detach the partition no longer points at the primary, it carries
`IDetachedPartition` (and loses `IAnalysisRequestPartition`), and the
`DetachedFrom` reference points back at the primary:

    >>> partition.getParentAnalysisRequest() is None
    True
    >>> IDetachedPartition.providedBy(partition)
    True
    >>> IAnalysisRequestPartition.providedBy(partition)
    False
    >>> partition.getDetachedFrom() == primary
    True


Reattach the partition
......................

The guard accepts the transition because the primary is still
reachable and both samples are in the same review state:

    >>> isTransitionAllowed(partition, "reattach")
    True

    >>> success, message = do_action_for(partition, "reattach")
    >>> success
    True

After reattach the link to the primary is restored, the markers are
swapped back, and `DetachedFrom` is cleared:

    >>> partition.getParentAnalysisRequest() == primary
    True
    >>> IAnalysisRequestPartition.providedBy(partition)
    True
    >>> IDetachedPartition.providedBy(partition)
    False
    >>> partition.getDetachedFrom() is None
    True


Guard rejects when the partition is not detached
................................................

A fresh partition has never been detached, so `reattach` is not
allowed:

    >>> fresh = create_partition(primary, request, primary.getAnalyses())
    >>> IDetachedPartition.providedBy(fresh)
    False
    >>> isTransitionAllowed(fresh, "reattach")
    False


Reattach coexists with siblings created in the meantime
.......................................................

Building on the previous step, the partition is detached again,
a fresh partition is created on the primary (which picks up the
next counter value), and the detached one is then reattached.
Both partitions must coexist with unique IDs:

    >>> _ = do_action_for(partition, "detach")
    >>> partition_id = partition.getId()
    >>> sibling = create_partition(primary, request, primary.getAnalyses())
    >>> sibling.getId() != partition_id
    True
    >>> success, message = do_action_for(partition, "reattach")
    >>> success
    True
    >>> partition.getParentAnalysisRequest() == primary
    True

The reattached partition coexists with the partitions that were
created in the meantime — both `fresh` (from the previous step) and
`sibling`:

    >>> descendant_ids = sorted(d.getId() for d in primary.getDescendants())
    >>> expected = sorted(
    ...     [partition_id, fresh.getId(), sibling.getId()])
    >>> descendant_ids == expected
    True

The partition's original ID survives the round-trip — `reattach`
only restores the parent link, it does not rename:

    >>> partition.getId() == partition_id
    True


Guard rejects when parent and detached sample drift apart
.........................................................

Detach the partition again, then push the primary into a different
review state. The guard must refuse the transition:

    >>> _ = do_action_for(partition, "detach")
    >>> IDetachedPartition.providedBy(partition)
    True
    >>> api.get_workflow_status_of(partition)
    'sample_received'

Move the primary to `to_be_verified` without touching the detached
partition:

    >>> from bika.lims.utils import changeWorkflowState
    >>> _ = changeWorkflowState(
    ...     primary, "senaite_sample_workflow", "to_be_verified")
    >>> api.get_workflow_status_of(primary)
    'to_be_verified'

States differ — the guard rejects reattach:

    >>> isTransitionAllowed(partition, "reattach")
    False
