Sample dispose
--------------

The `dispose` workflow transition moves a received sample (and its
partitions) into the `disposed` state, mirroring the existing
`dispatch` workflow. The transition is gated by a global
`dispose_workflow_enabled` setup flag (disabled by default) and by a
guard that blocks disposal while an analysis is assigned to a
worksheet. A disposed sample can be brought back with `restore`.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t SampleDispose


Test Setup
..........

Imports:

    >>> from DateTime import DateTime
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.analysisrequest import create_partition
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import isTransitionAllowed

Functional helpers:

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

    >>> def receive(sample):
    ...     do_action_for(sample, "receive")
    ...     return api.get_workflow_status_of(sample)

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


Helper to create and receive a sample
.....................................

    >>> def new_sample(services):
    ...     values = {
    ...         "Client": client.UID(),
    ...         "Contact": contact.UID(),
    ...         "SamplingDate": date_now,
    ...         "DateSampled": date_now,
    ...         "SampleType": sampletype.UID(),
    ...     }
    ...     sample = create_analysisrequest(client, request, values, services)
    ...     receive(sample)
    ...     return sample


The toggle gates the transition
...............................

The `dispose_workflow_enabled` flag is disabled by default:

    >>> senaite_setup = api.get_senaite_setup()
    >>> senaite_setup.getDisposeWorkflowEnabled()
    False

With the flag disabled the `dispose` transition is not offered, even
on a received sample:

    >>> sample = new_sample([service.UID()])
    >>> api.get_workflow_status_of(sample)
    'sample_received'

    >>> isTransitionAllowed(sample, "dispose")
    False

    >>> succeeded, message = do_action_for(sample, "dispose")
    >>> succeeded
    False

Enabling the flag makes the transition available:

    >>> senaite_setup.setDisposeWorkflowEnabled(True)
    >>> isTransitionAllowed(sample, "dispose")
    True


Dispose and restore a sample
............................

Disposing the sample moves it to the `disposed` state and marks it with
the `IDisposed` interface:

    >>> from senaite.core.interfaces import IDisposed
    >>> succeeded, message = do_action_for(sample, "dispose")
    >>> succeeded
    True

    >>> api.get_workflow_status_of(sample)
    'disposed'

    >>> IDisposed.providedBy(sample)
    True

Restoring brings the sample back to the state it was in before and
removes the marker:

    >>> succeeded, message = do_action_for(sample, "restore")
    >>> succeeded
    True

    >>> api.get_workflow_status_of(sample)
    'sample_received'

    >>> IDisposed.providedBy(sample)
    False


Disposing a sample locks its analyses
......................................

Disposing a sample transitions its analyses to the read-only `locked`
state, so their results can no longer be edited by any surface (listing,
JSON API, ...) because the edit permissions are revoked at the object
level.

    >>> from senaite.core.permissions import EditResults

A received sample has editable analyses:

    >>> sample = new_sample([service.UID()])
    >>> analysis = sample.getAnalyses(full_objects=True)[0]
    >>> api.get_workflow_status_of(analysis)
    'unassigned'
    >>> from bika.lims.api.security import check_permission
    >>> check_permission(EditResults, analysis)
    True

Disposing the sample locks the analysis:

    >>> succeeded, message = do_action_for(sample, "dispose")
    >>> api.get_workflow_status_of(sample)
    'disposed'
    >>> api.get_workflow_status_of(analysis)
    'locked'
    >>> check_permission(EditResults, analysis)
    False

Locked analyses are still listed together with the active ones (the
"Valid" review state), so they do not disappear from the sample view:

    >>> from bika.lims.browser.analyses.view import AnalysesView
    >>> aview = AnalysesView(sample, request)
    >>> valid = [rs for rs in aview.review_states if rs["id"] == "default"][0]
    >>> "locked" in valid["contentFilter"]["review_state"]
    True

Restoring the sample brings the analysis back to its previous status and
makes it editable again:

    >>> succeeded, message = do_action_for(sample, "restore")
    >>> api.get_workflow_status_of(sample)
    'sample_received'
    >>> api.get_workflow_status_of(analysis)
    'unassigned'
    >>> check_permission(EditResults, analysis)
    True

The `lock` transition cannot be triggered manually on an analysis whose
sample is not in a locking state:

    >>> from bika.lims.workflow import isTransitionAllowed as is_allowed
    >>> is_allowed(analysis, "lock")
    False


The guard blocks disposal of worksheet-assigned analyses
........................................................

When an analysis of the sample is assigned to a worksheet, the
sample can no longer be disposed:

    >>> ws_sample = new_sample([service.UID()])
    >>> analyses = ws_sample.getAnalyses(full_objects=True)
    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> for analysis in analyses:
    ...     worksheet.addAnalysis(analysis)
    >>> api.get_workflow_status_of(analyses[0])
    'assigned'

    >>> isTransitionAllowed(ws_sample, "dispose")
    False

Removing the analysis from the worksheet releases the guard:

    >>> for analysis in analyses:
    ...     worksheet.removeAnalysis(analysis)
    >>> isTransitionAllowed(ws_sample, "dispose")
    True


Dispose propagates to partitions
................................

Create a primary sample with a partition:

    >>> primary = new_sample([service.UID()])
    >>> partition = create_partition(primary, request, primary.getAnalyses())
    >>> receive(partition)
    'sample_received'
    >>> part_analysis = partition.getAnalyses(full_objects=True)[0]

Disposing the primary propagates the transition to the partition:

    >>> succeeded, message = do_action_for(primary, "dispose")
    >>> succeeded
    True

    >>> api.get_workflow_status_of(primary)
    'disposed'

    >>> api.get_workflow_status_of(partition)
    'disposed'

The analyses of the partition (child sample) are locked as well, not just
those of the primary:

    >>> api.get_workflow_status_of(part_analysis)
    'locked'

Restoring the primary restores its partitions too:

    >>> succeeded, message = do_action_for(primary, "restore")
    >>> succeeded
    True

    >>> api.get_workflow_status_of(primary)
    'sample_received'

    >>> api.get_workflow_status_of(partition)
    'sample_received'

And the partition analyses are brought back to their previous status:

    >>> api.get_workflow_status_of(part_analysis)
    'unassigned'


Primary is auto-disposed when all partitions are disposed
.........................................................

Disposing every partition promotes the primary to `disposed`:

    >>> succeeded, message = do_action_for(partition, "dispose")
    >>> succeeded
    True

    >>> api.get_workflow_status_of(partition)
    'disposed'

    >>> api.get_workflow_status_of(primary)
    'disposed'


Permission enforcement
......................

The `dispose` transition is guarded by the
`senaite.core: Transition: Dispose Sample` permission. A user without
that permission cannot dispose a sample:

    >>> disposable = new_sample([service.UID()])
    >>> setRoles(portal, TEST_USER_ID, ['Authenticated'])
    >>> isTransitionAllowed(disposable, "dispose")
    False

Restore the Lab Manager roles:

    >>> setRoles(portal, TEST_USER_ID, ['Manager', 'LabManager'])
    >>> isTransitionAllowed(disposable, "dispose")
    True

Re-disable the dispose workflow to leave the setup untouched:

    >>> senaite_setup.setDisposeWorkflowEnabled(False)
