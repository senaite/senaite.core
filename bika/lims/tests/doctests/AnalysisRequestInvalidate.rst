Analysis Request invalidate
===========================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t AnalysisRequestInvalidate


Test Setup
----------

Needed Imports:

    >>> from DateTime import DateTime
    >>> from plone import api as ploneapi

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for


Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)


Variables:

    >>> date_now = timestamp()
    >>> browser = self.getBrowser()
    >>> portal = self.portal
    >>> request = self.request
    >>> bika_setup = portal.bika_setup
    >>> bika_sampletypes = bika_setup.bika_sampletypes
    >>> bika_samplepoints = bika_setup.bika_samplepoints
    >>> bika_analysiscategories = bika_setup.bika_analysiscategories
    >>> bika_analysisservices = bika_setup.bika_analysisservices
    >>> bika_labcontacts = bika_setup.bika_labcontacts
    >>> bika_storagelocations = bika_setup.bika_storagelocations
    >>> bika_samplingdeviations = bika_setup.bika_samplingdeviations
    >>> bika_sampleconditions = bika_setup.bika_sampleconditions
    >>> portal_url = portal.absolute_url()
    >>> bika_setup_url = portal_url + "/bika_setup"

Test user:

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager.

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager', 'LabManager',])


Create Analysis Requests (AR)
-----------------------------

An `AnalysisRequest` can only be created inside a `Client`:

    >>> clients = self.portal.clients
    >>> client = api.create(clients, "Client", Name="NARALABS", ClientID="JG")
    >>> client
    <Client at /plone/clients/client-1>

To create a new AR, a `Contact` is needed:

    >>> contact = api.create(client, "Contact", Firstname="Juan", Surname="Gallostra")
    >>> contact
    <Contact at /plone/clients/client-1/contact-1>

A `SampleType` defines how long the sample can be retained, the minimum volume
needed, if it is hazardous or not, the point where the sample was taken etc.:

    >>> sampletype = api.create(bika_sampletypes, "SampleType", Prefix="water", MinimumVolume="100 ml")
    >>> sampletype
    <SampleType at /plone/bika_setup/bika_sampletypes/sampletype-1>

A `SamplePoint` defines the location, where a `Sample` was taken:

    >>> samplepoint = api.create(bika_samplepoints, "SamplePoint", title="Lake of Constance")
    >>> samplepoint
    <SamplePoint at /plone/bika_setup/bika_samplepoints/samplepoint-1>

An `AnalysisCategory` categorizes different `AnalysisServices`:

    >>> analysiscategory = api.create(bika_analysiscategories, "AnalysisCategory", title="Water")
    >>> analysiscategory
    <AnalysisCategory at /plone/bika_setup/bika_analysiscategories/analysiscategory-1>

An `AnalysisService` defines a analysis service offered by the laboratory:

    >>> analysisservice = api.create(bika_analysisservices, "AnalysisService", title="PH", ShortTitle="ph", Category=analysiscategory, Keyword="PH")
    >>> analysisservice
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-1>

Finally, the `AnalysisRequest` can be created:

    >>> values = {
    ...           'Client': client.UID(),
    ...           'Contact': contact.UID(),
    ...           'SamplingDate': date_now,
    ...           'DateSampled': date_now,
    ...           'SampleType': sampletype.UID(),
    ...           'Priority': '1',
    ...          }

    >>> service_uids = [analysisservice.UID()]
    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar
    <AnalysisRequest at /plone/clients/client-1/water-0001>

Also, make sure that the Analysis Request only has one analysis. You will
see why later:

    >>> len(ar.getAnalyses())
    1


Submit Analyses results for the current Analysis Request
--------------------------------------------------------

First transition the Analysis Request to received:

    >>> transitioned = do_action_for(ar, 'receive')
    >>> transitioned[0]
    True
    >>> api.get_workflow_status_of(ar)
    'sample_received'

Set the results of the Analysis and transition them for verification:

    >>> for analysis in ar.getAnalyses(full_objects=True):
    ...     analysis.setResult('12')
    ...     transitioned = do_action_for(analysis, 'submit')
    >>> transitioned[0]
    True

Check that both the Analysis Request and its analyses have been transitioned
to 'to_be_verified':

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'
    >>> not_to_be_verified = 0
    >>> for analysis in ar.getAnalyses(full_objects=True):
    ...     if api.get_workflow_status_of(analysis) != 'to_be_verified':
    ...         not_to_be_verified += 1
    >>> not_to_be_verified
    0


Verify Analyses results for the current Analysis Request
--------------------------------------------------------

Same user cannot verify by default:

    >>> ar.bika_setup.setSelfVerificationEnabled(True)

Select all analyses from the Analysis Request and verify them:

    >>> for analysis in ar.getAnalyses(full_objects=True):
    ...     transitioned = do_action_for(analysis, 'verify')
    >>> transitioned[0]
    True

Check that both the Analysis Request analyses have been transitioned to
`verified`:

    >>> api.get_workflow_status_of(ar)
    'verified'
    >>> not_verified = 0
    >>> for analysis in ar.getAnalyses(full_objects=True):
    ...     if api.get_workflow_status_of(analysis) != 'verified':
    ...         not_verified += 1
    >>> not_verified
    0


Invalidate the Analysis Request
-------------------------------

When an Analysis Request is invalidated two things should happen:

    1- The Analysis Request is transitioned to 'invalid'. Analyses remain in
    `verified` state.

    2- A new Analysis Request (retest) is created automatically, with same
    analyses as the invalidated, but in `sample_received` state.

Invalidate the Analysis Request:

    >>> transitioned = do_action_for(ar, 'invalidate')
    >>> transitioned[0]
    True
    >>> api.get_workflow_status_of(ar)
    'invalid'
    >>> ar.isInvalid()
    True

Verify a new Analysis Request (retest) has been created, with same analyses as
the invalidated:

    >>> retest = ar.getRetest()
    >>> retest
    <AnalysisRequest at /plone/clients/client-1/water-0001-R01>

    >>> retest.getInvalidated()
    <AnalysisRequest at /plone/clients/client-1/water-0001>

    >>> api.get_workflow_status_of(retest)
    'sample_received'

    >>> retest_ans = map(lambda an: an.getKeyword(), retest.getAnalyses(full_objects=True))
    >>> invalid_ans = map(lambda an: an.getKeyword(), ar.getAnalyses(full_objects=True))
    >>> len(set(retest_ans)-set(invalid_ans))
    0


Invalidate the retest
---------------------

We can even invalidate the retest generated previously. As a result, a new
retest will be created.

First, submit all analyses from the retest:

    >>> for analysis in retest.getAnalyses(full_objects=True):
    ...     analysis.setResult(12)
    ...     transitioned = do_action_for(analysis, 'submit')
    >>> transitioned[0]
    True

    >>> api.get_workflow_status_of(retest)
    'to_be_verified'

Now, verify all analyses from the retest:

    >>> for analysis in retest.getAnalyses(full_objects=True):
    ...     transitioned = do_action_for(analysis, 'verify')
    >>> transitioned[0]
    True

    >>> not_verified = 0
    >>> for analysis in retest.getAnalyses(full_objects=True):
    ...     if api.get_workflow_status_of(analysis) != 'verified':
    ...         not_verified += 1
    >>> not_verified
    0

    >>> api.get_workflow_status_of(retest)
    'verified'

Invalidate the Retest:

    >>> transitioned = do_action_for(retest, 'invalidate')
    >>> transitioned[0]
    True
    >>> api.get_workflow_status_of(retest)
    'invalid'
    >>> retest.isInvalid()
    True

Verify a new Analysis Request (retest 2) has been created, with same analyses
as the invalidated (retest):

    >>> retest2 = retest.getRetest()
    >>> retest2
    <AnalysisRequest at /plone/clients/client-1/water-0001-R02>

    >>> retest2.getInvalidated()
    <AnalysisRequest at /plone/clients/client-1/water-0001-R01>

    >>> retest2.getInvalidated().getInvalidated()
    <AnalysisRequest at /plone/clients/client-1/water-0001>

    >>> api.get_workflow_status_of(retest2)
    'sample_received'

    >>> not_registered = 0
    >>> for analysis in retest2.getAnalyses(full_objects=True):
    ...     if api.get_workflow_status_of(analysis) != 'unassigned':
    ...         registered += 1
    >>> not_registered
    0

    >>> retest_ans = map(lambda an: an.getKeyword(), retest2.getAnalyses(full_objects=True))
    >>> invalid_ans = map(lambda an: an.getKeyword(), retest.getAnalyses(full_objects=True))
    >>> len(set(retest_ans)-set(invalid_ans))
    0
