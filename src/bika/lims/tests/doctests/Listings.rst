Listings
========

Running this test from the buildout directory::

    bin/test test_textual_doctests -t Listings


Test Setup
----------

Imports:

    >>> from operator import methodcaller
    >>> from DateTime import DateTime

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest

Functional Helpers:

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

    >>> def create_ar(client, **kw):
    ...     values = {}
    ...     services = []
    ...     for k, v in kw.iteritems():
    ...         if k == "Services":
    ...             services = map(api.get_uid, v)
    ...         elif api.is_object(v):
    ...             values[k] = api.get_uid(v)
    ...         else:
    ...             values[k] = v
    ...     return create_analysisrequest(client, self.request, values, services)

Variables::

    >>> date_now = timestamp()
    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.bika_setup

Test User:

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])


Prepare Test Environment
------------------------

Setupitems:

    >>> clients = portal.clients
    >>> sampletypes = setup.bika_sampletypes
    >>> samplepoints = setup.bika_samplepoints
    >>> analysiscategories = setup.bika_analysiscategories
    >>> analysisservices = setup.bika_analysisservices

Create Clients:

    >>> cl1 = api.create(clients, "Client", Name="Client1", ClientID="C1")
    >>> cl2 = api.create(clients, "Client", Name="Client2", ClientID="C2")
    >>> cl3 = api.create(clients, "Client", Name="Client3", ClientID="C3")

Create some Contact(s):

    >>> c1 = api.create(cl1, "Contact", Firstname="Client", Surname="1")
    >>> c2 = api.create(cl2, "Contact", Firstname="Client", Surname="2")
    >>> c3 = api.create(cl3, "Contact", Firstname="Client", Surname="3")

Create some Sample Types:

    >>> st1 = api.create(sampletypes, "SampleType", Prefix="s1", MinimumVolume="100 ml")
    >>> st2 = api.create(sampletypes, "SampleType", Prefix="s2", MinimumVolume="200 ml")
    >>> st3 = api.create(sampletypes, "SampleType", Prefix="s3", MinimumVolume="300 ml")

Create some Sample Points:

    >>> sp1 = api.create(samplepoints, "SamplePoint", title="Sample Point 1")
    >>> sp2 = api.create(samplepoints, "SamplePoint", title="Sample Point 2")
    >>> sp3 = api.create(samplepoints, "SamplePoint", title="Sample Point 3")

Create some Analysis Categories:

    >>> ac1 = api.create(analysiscategories, "AnalysisCategory", title="Analysis Category 1")
    >>> ac2 = api.create(analysiscategories, "AnalysisCategory", title="Analysis Category 2")
    >>> ac3 = api.create(analysiscategories, "AnalysisCategory", title="Analysis Category 3")

Create some Analysis Services:

    >>> as1 = api.create(analysisservices, "AnalysisService", title="Analysis Service 1", ShortTitle="AS1", Category=ac1, Keyword="AS1", Price="10")
    >>> as2 = api.create(analysisservices, "AnalysisService", title="Analysis Service 2", ShortTitle="AS1", Category=ac2, Keyword="AS1", Price="20")
    >>> as3 = api.create(analysisservices, "AnalysisService", title="Analysis Service 3", ShortTitle="AS1", Category=ac3, Keyword="AS1", Price="30")

Create some Analysis Requests:

    >>> ar11 = create_ar(cl1, Contact=c1, SamplingDate=date_now, DateSampled=date_now, SampleType=st1, Priority='1', Services=[as1])
    >>> ar12 = create_ar(cl1, Contact=c1, SamplingDate=date_now, DateSampled=date_now, SampleType=st1, Priority='2', Services=[as1])
    >>> ar13 = create_ar(cl1, Contact=c1, SamplingDate=date_now, DateSampled=date_now, SampleType=st1, Priority='3', Services=[as1])

    >>> ar21 = create_ar(cl2, Contact=c2, SamplingDate=date_now, DateSampled=date_now, SampleType=st2, Priority='1', Services=[as2])
    >>> ar22 = create_ar(cl2, Contact=c2, SamplingDate=date_now, DateSampled=date_now, SampleType=st2, Priority='2', Services=[as2])
    >>> ar23 = create_ar(cl2, Contact=c2, SamplingDate=date_now, DateSampled=date_now, SampleType=st2, Priority='3', Services=[as2])

    >>> ar31 = create_ar(cl3, Contact=c3, SamplingDate=date_now, DateSampled=date_now, SampleType=st3, Priority='1', Services=[as3])
    >>> ar32 = create_ar(cl3, Contact=c3, SamplingDate=date_now, DateSampled=date_now, SampleType=st3, Priority='2', Services=[as3])
    >>> ar33 = create_ar(cl3, Contact=c3, SamplingDate=date_now, DateSampled=date_now, SampleType=st3, Priority='3', Services=[as3])


Listing View
------------


    >>> from bika.lims.browser.bika_listing import BikaListingView
    >>> context = portal.analysisrequests
    >>> request = self.request
    >>> listing = BikaListingView(context, request)
    >>> listing
    <bika.lims.browser.bika_listing.BikaListingView object at 0x...>

Setup the view to behave like the `AnalysisRequestsView`:

    >>> from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING

    >>> listing.catalog = CATALOG_ANALYSIS_REQUEST_LISTING
    >>> listing.contentFilter = {
    ...     'sort_on': 'created',
    ...     'sort_order': 'reverse',
    ...     'path': {"query": "/", "level": 0},
    ...     'is_active': True,}

The listing view should now return all created ARs:

    >>> results = listing.search()
    >>> len(results)
    9

Searching for a value should work:

    >>> results = listing.search(searchterm="s1")
    >>> len(results)
    3

    >>> map(lambda x: x.getObject().getSampleType().getPrefix(), results)
    ['s1', 's1', 's1']

    >>> results = listing.search(searchterm="client-3")
    >>> map(lambda x: x.getObject().getClient(), results)
    [<Client at /plone/clients/client-3>, <Client at /plone/clients/client-3>, <Client at /plone/clients/client-3>]
