Analysis Request Workflow
=========================

End-to-end testing of AnalysisRequest and related workflows.

In AnalysisRequest/Sample/Analysis workflows there are many interdependencies,
this file is intended to test all possible configurations and settings.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t AnalysisRequestWorkflow


Test Setup
----------

Needed Imports:

.. code-block:: python

    >>> from DateTime import DateTime
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from bika.lims.workflow import getCurrentState


Functional Helpers:

.. code-block:: python

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return 'http://{}:{}/{}'.format(ip, port, portal.id)

    >>> def timestamp(format='%Y-%m-%d'):
    ...     return DateTime().strftime(format)

    >>> def getstates(ar):
    ...     arstate = getCurrentState(ar)
    ...     anstate = getCurrentState(ar.getAnalyses()[0].getObject())
    ...     samplestate = getCurrentState(ar.getSample())
    ...     part = ar.getSample().objectValues('SamplePartition')[0]
    ...     partstate = getCurrentState(part)
    ...     return "AR: '%s', Analyses: '%s', Sample: '%s', Partition: '%s'" % \
    ...            (arstate, anstate, samplestate, partstate)


Variables:

.. code-block:: python

    >>> date_now = timestamp()
    >>> portal = self.portal
    >>> request = self.request
    >>> bika_setup = portal.bika_setup
    >>> bika_labcontacts = bika_setup.bika_labcontacts
    >>> bika_sampletypes = bika_setup.bika_sampletypes
    >>> bika_analysiscategories = bika_setup.bika_analysiscategories
    >>> bika_analysisservices = bika_setup.bika_analysisservices


Test user:

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager:

.. code-block:: python

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])


Setup data required before creating ARs
----------------------------------------

This is a test for the 'receive' guard on samples, ARs, and analyses, where
these two settings play against each other.

An `AnalysisRequest` can only be created inside a `Client`:

.. code-block:: python

    >>> clients = self.portal.clients
    >>> client = api.create(clients, 'Client', Name='Happy Hills', ClientID='RB')


To create a new AR, a `Contact` is needed:

.. code-block:: python

    >>> contact = api.create(client, 'Contact', Firstname='Rita', Surname='Mohale')


We're using the SamplingWorkflowEnabled in these tests, so we need a Sampler.  For
this we must first create a login user, then a labcontact, and then associate
the two:

.. code-block:: python

    >>> member = portal.portal_registration.addMember('sampler1', 'sampler1',
    ...              properties={'username': 'sampler1',
    ...                          'email': 'sampler1@example.com',
    ...                          'fullname': 'Sampler One'})
    >>> setRoles(portal, 'sampler1', ['Sampler'])
    >>> sampler = api.create(bika_labcontacts, 'LabContact', Firstname='Sampler', Surname='One')
    >>> sampler.setUser(member)
    True


A `SampleType` defines how long the sample can be retained, the minimum volume
needed, if it is hazardous or not, the point where the sample was taken etc:

.. code-block:: python

    >>> sampletype = api.create(bika_sampletypes, 'SampleType', Prefix='water')


An `AnalysisCategory` categorizes different `AnalysisServices`:

.. code-block:: python

    >>> analysiscategory = api.create(bika_analysiscategories, 'AnalysisCategory', title='Water')


An `AnalysisService` defines an analysis offered by the laboratory.  For the
purposes of testing workflow, we only need to add simple services, requiring
only a single result value to be entered:

.. code-block:: python

    >>> service1 = api.create(bika_analysisservices, 'AnalysisService', title='PH', Category=analysiscategory, Keyword='PH')
    >>> service2 = api.create(bika_analysisservices, 'AnalysisService', title='Calcium', Category=analysiscategory, Keyword='CA')


Most ARs in this text will be created with these starting values:

.. code-block:: python

    >>> values = {
    ...     'Client': client.UID(),
    ...     'Contact': contact.UID(),
    ...     'SamplingDate': date_now,
    ...     'DateSampled': date_now,
    ...     'SampleType': sampletype.UID(),
    ...     'Priority': '1',
    ...     'Analyses': [service1.UID(), service2.UID()],
    ... }


Standard AR/Sample/Analysis workflow
------------------------------------

receive -> submit -> retract -> verify -> publish

.. code-block:: python

    >>> bika_setup.setSamplingWorkflowEnabled(False)
    >>> bika_setup.setAutoReceiveSamples(False)
    >>> ar = create_analysisrequest(client, request, values)
    >>> getstates(ar)
    "AR: 'sample_due', Analyses: 'sample_due', Sample: 'sample_due', Partition: 'sample_due'"
    >>> p = doActionFor(ar, 'receive')
    >>> getstates(ar)
    "AR: 'sample_received', Analyses: 'sample_received', Sample: 'sample_received', Partition: 'sample_received'"



Standard workflow when adding a new AR to an existing sample
------------------------------------------------------------

Sampling Workflow
-----------------

Verify that AutoReceiveSamples and SamplingWorkflowEnabled settings play nicely
-------------------------------------------------------------------------------

There are six possible conditions tested here:

 +=========================+==============+====================+==============+
 | SamplingWorkflowEnabled | review_state | AutoReceiveSamples | Guard result |
 +=========================+==============+====================+==============+
1| Enabled                 | registered   | Enabled            | False        |
2| Enabled                 | due          | Enabled            | True         |
3| Enabled                 | registered   | Disabled           | False        |
4| Enabled                 | due          | Disabled           | False        |
5| Disabled                | registered   | Enabled            | True         |
6| Disabled                | registered   | Disabled           | False        |
 +=========================+==============+====================+==============+

Case 1:  SamplingWorkflowEnabled True, AutoReceiveSamples True.

This should have no effect during the `registered` state,
all items should be in `to_be_sampled` after creation.

.. code-block:: python

    >>> bika_setup.setSamplingWorkflowEnabled(True)
    >>> bika_setup.setAutoReceiveSamples(True)
    >>> ar = create_analysisrequest(client, request, values)
    >>> getstates(ar)
    "AR: 'to_be_sampled', Analyses: 'to_be_sampled', Sample: 'to_be_sampled', Partition: 'to_be_sampled'"

Case 2:  SamplingWorkflowEnabled True, AutoReceiveSamples True.

Once the `sample` transition is completed, all items should
automatically be transitioned to `sample_received`:

.. code-block:: python

    >>> ar.setSampler(sampler)
    >>> ar.setDateSampled(timestamp())
    >>> p = doActionFor(ar, 'sample')
    >>> getstates(ar)
    "AR: 'sample_received', Analyses: 'sample_received', Sample: 'sample_received', Partition: 'sample_received'"

Case 3 and 4: SamplingWorkflowEnabled True, AutoReceiveSamples False.

.. code-block:: python

    >>> bika_setup.setSamplingWorkflowEnabled(True)
    >>> bika_setup.setAutoReceiveSamples(False)
    >>> ar = create_analysisrequest(client, request, values)
    >>> getstates(ar)
    "AR: 'to_be_sampled', Analyses: 'to_be_sampled', Sample: 'to_be_sampled', Partition: 'to_be_sampled'"

    >>> ar.setSampler(sampler)
    >>> ar.setDateSampled(timestamp())
    >>> p = doActionFor(ar, 'sample')
    >>> getstates(ar)
    "AR: 'sample_due', Analyses: 'sample_due', Sample: 'sample_due', Partition: 'sample_due'"

Case 5: `SamplingWorkflowEnabled` is off, `AutoReceiveSamples` is on.
This means the objects should begin their lives in state 'sample_received'

.. code-block:: python

    >>> bika_setup.setSamplingWorkflowEnabled(False)
    >>> bika_setup.setAutoReceiveSamples(True)
    >>> ar = create_analysisrequest(client, request, values)
    >>> getstates(ar)
    "AR: 'sample_received', Analyses: 'sample_received', Sample: 'sample_received', Partition: 'sample_received'"
    >>> import time
    >>> time.sleep(1)


Case 6: Both settings are off.  The items should start in `sample_due` state.

.. code-block:: python

    >>> bika_setup.setSamplingWorkflowEnabled(False)
    >>> bika_setup.setAutoReceiveSamples(False)
    >>> ar = create_analysisrequest(client, request, values)
    >>> getstates(ar)
    "AR: 'sample_due', Analyses: 'sample_due', Sample: 'sample_due', Partition: 'sample_due'"
