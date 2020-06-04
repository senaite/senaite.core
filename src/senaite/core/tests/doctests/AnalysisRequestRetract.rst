Analysis Request retract
========================

Running this test from the buildout directory::

    bin/test test_textual_doctests -t AnalysisRequestRetract


Test Setup
----------

Needed Imports::

    >>> import transaction
    >>> from DateTime import DateTime
    >>> from plone import api as ploneapi

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for


Functional Helpers::

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)


Variables::

    >>> date_now = timestamp()
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

Test user::

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager.

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])


Create Analysis Requests (AR)
-----------------------------

An `AnalysisRequest` can only be created inside a `Client`::

    >>> clients = self.portal.clients
    >>> client = api.create(clients, "Client", Name="NARALABS", ClientID="JG")
    >>> client
    <Client at /plone/clients/client-1>

To create a new AR, a `Contact` is needed::

    >>> contact = api.create(client, "Contact", Firstname="Juan", Surname="Gallostra")
    >>> contact
    <Contact at /plone/clients/client-1/contact-1>

A `SampleType` defines how long the sample can be retained, the minimum volume
needed, if it is hazardous or not, the point where the sample was taken etc.::

    >>> sampletype = api.create(bika_sampletypes, "SampleType", Prefix="water", MinimumVolume="100 ml")
    >>> sampletype
    <SampleType at /plone/bika_setup/bika_sampletypes/sampletype-1>

A `SamplePoint` defines the location, where a `Sample` was taken::

    >>> samplepoint = api.create(bika_samplepoints, "SamplePoint", title="Lake of Constance")
    >>> samplepoint
    <SamplePoint at /plone/bika_setup/bika_samplepoints/samplepoint-1>

An `AnalysisCategory` categorizes different `AnalysisServices`::

    >>> analysiscategory = api.create(bika_analysiscategories, "AnalysisCategory", title="Water")
    >>> analysiscategory
    <AnalysisCategory at /plone/bika_setup/bika_analysiscategories/analysiscategory-1>

An `AnalysisService` defines a analysis service offered by the laboratory::

    >>> analysisservice = api.create(bika_analysisservices, "AnalysisService", title="PH", ShortTitle="ph", Category=analysiscategory, Keyword="PH")
    >>> analysisservice
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-1>

Finally, the `AnalysisRequest` can be created::

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
see why later::

    >>> len(ar.getAnalyses())
    1


Submit Analyses results for the current Analysis Request
--------------------------------------------------------

First transition the Analysis Request to received::

    >>> transitioned = do_action_for(ar, 'receive')
    >>> transitioned[0]
    True
    >>> ar.portal_workflow.getInfoFor(ar, 'review_state')
    'sample_received'

Set the results of the Analysis and transition them for verification::

    >>> for analysis in ar.getAnalyses(full_objects=True):
    ...     analysis.setResult('12')
    ...     transitioned = do_action_for(analysis, 'submit')
    >>> transitioned[0]
    True

Check that both the Analysis Request and its analyses have been transitioned
to 'to_be_verified'::

    >>> ar.portal_workflow.getInfoFor(ar, 'review_state')
    'to_be_verified'
    >>> not_to_be_verified = 0
    >>> for analysis in ar.getAnalyses(full_objects=True):
    ...     if analysis.portal_workflow.getInfoFor(analysis, 'review_state') != 'to_be_verified':
    ...         not_to_be_verified += 1
    >>> not_to_be_verified
    0


Retract the Analysis Request
----------------------------
When an Analysis Request is retracted two things should happen:

    1- The Analysis Request is transitioned to 'sample_received'. Since
    the results have been retracted its review state goes back to just
    before the submission of results.

    2- Its current analyses are transitioned to 'retracted' and a duplicate
    of each analysis is created (so that results can be introduced again) with
    review state 'sample_received'.

Retract the Analysis Request::

    >>> transitioned = do_action_for(ar, 'retract')
    >>> transitioned[0]
    True
    >>> ar.portal_workflow.getInfoFor(ar, 'review_state')
    'sample_received'

Verify that its analyses have also been retracted and that a new analysis has been
created with review status 'unassigned'. Since we previously checked that the AR
had only one analyses the count for both 'retracted' and 'unassigned' analyses
should be one::

    >>> registered = 0
    >>> retracted = 0
    >>> for analysis in ar.getAnalyses(full_objects=True):
    ...     if analysis.portal_workflow.getInfoFor(analysis, 'review_state') == 'retracted':
    ...         retracted += 1
    ...     if analysis.portal_workflow.getInfoFor(analysis, 'review_state') != 'unassigned':
    ...         registered += 1
    >>> registered
    1
    >>> retracted
    1

