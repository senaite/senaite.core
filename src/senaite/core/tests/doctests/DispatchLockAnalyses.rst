Lock analyses on dispatch
-------------------------

Dispatching a sample marks it with the `IDispatched` interface and can
optionally lock its analyses, reusing the same `locked` analysis state as
the dispose workflow. The locking is gated by the `lock_analyses_on_dispatch`
setup flag (disabled by default). When a dispatched sample is restored, its
analyses are brought back to their previous status.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t DispatchLockAnalyses


Test Setup
..........

Imports:

    >>> from DateTime import DateTime
    >>> from bika.lims import api
    >>> from bika.lims.api.security import check_permission
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from senaite.core.interfaces import IDispatched
    >>> from senaite.core.permissions import EditResults

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
......................................

    >>> def new_sample():
    ...     values = {
    ...         "Client": client.UID(),
    ...         "Contact": contact.UID(),
    ...         "SamplingDate": date_now,
    ...         "DateSampled": date_now,
    ...         "SampleType": sampletype.UID(),
    ...     }
    ...     sample = create_analysisrequest(client, request, values,
    ...                                     [service.UID()])
    ...     receive(sample)
    ...     return sample


The flag is disabled by default
...............................

    >>> senaite_setup = api.get_senaite_setup()
    >>> senaite_setup.getLockAnalysesOnDispatch()
    False

With the flag disabled, dispatching a sample marks it as dispatched but
leaves its analyses editable:

    >>> sample = new_sample()
    >>> analysis = sample.getAnalyses(full_objects=True)[0]
    >>> succeeded, message = do_action_for(sample, "dispatch")
    >>> api.get_workflow_status_of(sample)
    'dispatched'
    >>> IDispatched.providedBy(sample)
    True
    >>> api.get_workflow_status_of(analysis)
    'unassigned'
    >>> check_permission(EditResults, analysis)
    True

The `lock` transition is not offered while the flag is disabled:

    >>> isTransitionAllowed(analysis, "lock")
    False

Restoring removes the marker:

    >>> succeeded, message = do_action_for(sample, "restore")
    >>> api.get_workflow_status_of(sample)
    'sample_received'
    >>> IDispatched.providedBy(sample)
    False


With the flag enabled, dispatch locks the analyses
...................................................

    >>> senaite_setup.setLockAnalysesOnDispatch(True)

    >>> sample = new_sample()
    >>> analysis = sample.getAnalyses(full_objects=True)[0]
    >>> succeeded, message = do_action_for(sample, "dispatch")
    >>> api.get_workflow_status_of(sample)
    'dispatched'
    >>> api.get_workflow_status_of(analysis)
    'locked'
    >>> check_permission(EditResults, analysis)
    False

Restoring the sample brings the analysis back to its previous status:

    >>> succeeded, message = do_action_for(sample, "restore")
    >>> api.get_workflow_status_of(sample)
    'sample_received'
    >>> api.get_workflow_status_of(analysis)
    'unassigned'
    >>> check_permission(EditResults, analysis)
    True

Re-disable the flag to leave the setup untouched:

    >>> senaite_setup.setLockAnalysesOnDispatch(False)
