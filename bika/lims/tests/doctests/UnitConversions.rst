===============
UnitConversions
===============

Analyses results are recorded in a given unit. Unit conversion allow for the reporting of a result in one or alternative units. Unit conversion are created a setup data that can be used on Reportig Units in Analysis Services.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t UnitConversions

Test Setup
==========
Needed Imports::

    >>> import transaction
    >>> from DateTime import DateTime
    >>> from plone import api as ploneapi
    >>> from zope.lifecycleevent import modified

    >>> from bika.lims import api
    >>> from bika.lims.idserver import renameAfterCreation
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest

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
    >>> portal_url = portal.absolute_url()
    >>> browser = self.getBrowser()
    >>> current_user = ploneapi.user.get_current()
    >>> ploneapi.user.grant_roles(user=current_user,roles = ['Manager'])
    >>> bika_analysiscategories = bika_setup.bika_analysiscategories
    >>> bika_analysisservices = bika_setup.bika_analysisservices

Test user::

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager.

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])



Client
======

A `client` lives in the `/clients` folder::

    >>> clients = portal.clients
    >>> client = api.create(clients, "Client", Name="RIDING BYTES", ClientID="RB")
    >>> client
    <Client at /plone/clients/client-1>

A `UnitConversion` lives in `/bika_setup/bika_unitconversions` folder.::

    >>> unitconversions = portal.bika_setup.bika_unitconversions
    >>> unitconv = api.create(unitconversions, "UnitConversion", title="mg/L", converted_unit="%", formula="Value * 100", description="mg/L to percentage")
    >>> renameAfterCreation(unitconv)
    'unitconversion-1'
    >>> unitconv
    <UnitConversion at /plone/bika_setup/bika_unitconversions/unitconversion-1>

A `SampleType` lives in `/bika_setup/bika_sampletypes` folder.::

    >>> sampletypes = portal.bika_setup.bika_sampletypes
    >>> sampletype = api.create(sampletypes, 'SampleType', title='Food')
    >>> sampletype
    <SampleType at /plone/bika_setup/bika_sampletypes/sampletype-1>

To create a new AR, a `Contact` is needed::

    >>> contact = api.create(client, "Contact", Firstname="Mike", Surname="Metcalfe")
    >>> contact
    <Contact at /plone/clients/client-1/contact-1>

An `AnalysisCategory` categorizes different `AnalysisServices`::

    >>> analysiscategory = api.create(bika_analysiscategories, "AnalysisCategory", title="Water")
    >>> analysiscategory
    <AnalysisCategory at /plone/bika_setup/bika_analysiscategories/analysiscategory-1>

An `AnalysisService` defines a analysis service offered by the laboratory::

    >>> analysisservice = api.create(bika_analysisservices, "AnalysisService", title="PH", ShortTitle="ph", Category=analysiscategory, Keyword="PH", Precision="2")
    >>> analysisservice
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-1>
    >>> analysisservice.setUnitConversions([{'ShowOnListing': '1', 'SampleType': sampletype.UID(), 'Unit': unitconv.UID()},])
    >>> len(analysisservice.getUnitConversions())
    1

A `AnalysisRequest` in `client-1` folder.::
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
    <AnalysisRequest at /plone/clients/client-1/0001-R01>
    >>> state = ploneapi.content.get_state(obj=ar, default='Unknown')
    >>> state
    'sample_due'
    >>> ploneapi.content.transition(obj=ar, transition='receive')
    >>> state = ploneapi.content.get_state(obj=ar, default='Unknown')
    >>> state
    'sample_received'
    >>> an = ar.getAnalyses()[0].getObject()
    >>> an.setResult(10)
    >>> an.getResult()
    '10'
    >>> current_user = ploneapi.user.get_current()
    >>> ploneapi.user.grant_roles(user=current_user,roles = ['Analyst'])
    >>> ploneapi.user.get_roles()
    ['Manager', 'Authenticated', 'Analyst']
    >>> an.setAnalyst(current_user.getUserName())
    >>> ploneapi.content.transition(obj=an, transition='submit')
    >>> state = ploneapi.content.get_state(obj=ar, default='Unknown')
    >>> state
    'to_be_verified'
    >>> from bika.lims.utils import resolve_unit
    >>> resolve_unit(an, an.getResult())
    '1000.00 %'
