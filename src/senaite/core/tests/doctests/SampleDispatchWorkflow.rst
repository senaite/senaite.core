Sample dispatch workflow
------------------------

The `dispatch` transition is gated by a global `dispatch_workflow_enabled`
setup flag (disabled by default), mirroring the dispose workflow. When a
sample is dispatched, it is marked with the `IDispatched` interface and its
analyses are transitioned to the read-only `locked` state. Restoring the
sample removes the marker and brings the analyses back to their previous
status.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t SampleDispatchWorkflow


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


The toggle gates the transition
...............................

The `dispatch_workflow_enabled` flag is disabled by default:

    >>> senaite_setup = api.get_senaite_setup()
    >>> senaite_setup.getDispatchWorkflowEnabled()
    False

With the flag disabled the `dispatch` transition is not offered, even on
a received sample:

    >>> sample = new_sample()
    >>> api.get_workflow_status_of(sample)
    'sample_received'

    >>> isTransitionAllowed(sample, "dispatch")
    False

    >>> succeeded, message = do_action_for(sample, "dispatch")
    >>> succeeded
    False

Enabling the flag makes the transition available:

    >>> senaite_setup.setDispatchWorkflowEnabled(True)
    >>> isTransitionAllowed(sample, "dispatch")
    True


Dispatch marks the sample and locks its analyses
.................................................

    >>> analysis = sample.getAnalyses(full_objects=True)[0]
    >>> succeeded, message = do_action_for(sample, "dispatch")
    >>> api.get_workflow_status_of(sample)
    'dispatched'
    >>> IDispatched.providedBy(sample)
    True

    >>> api.get_workflow_status_of(analysis)
    'locked'
    >>> check_permission(EditResults, analysis)
    False


Restore brings everything back
..............................

Restoring the sample removes the marker and unlocks the analyses:

    >>> succeeded, message = do_action_for(sample, "restore")
    >>> api.get_workflow_status_of(sample)
    'sample_received'
    >>> IDispatched.providedBy(sample)
    False

    >>> api.get_workflow_status_of(analysis)
    'unassigned'
    >>> check_permission(EditResults, analysis)
    True

Re-disable the dispatch workflow to leave the setup untouched:

    >>> senaite_setup.setDispatchWorkflowEnabled(False)
