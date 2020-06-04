Analysis Requests
=================

Analysis Requests in Bika LIMS describe an Analysis Order from a Client to the
Laboratory. Each Analysis Request manages a Sample, which holds the data of the
physical Sample from the Client. The Sample is currently not handled by its own
in Bika LIMS. So the managing Analysis Request is the primary interface from the
User (Client) to the Sample.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t AnalysisRequests


Test Setup
----------

Needed Imports::

    >>> import transaction
    >>> from DateTime import DateTime
    >>> from plone import api as ploneapi

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.api import do_transition_for

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


Analysis Requests (AR)
----------------------

An `AnalysisRequest` can only be created inside a `Client`::

    >>> clients = self.portal.clients
    >>> client = api.create(clients, "Client", Name="RIDING BYTES", ClientID="RB")
    >>> client
    <Client at /plone/clients/client-1>

To create a new AR, a `Contact` is needed::

    >>> contact = api.create(client, "Contact", Firstname="Ramon", Surname="Bartl")
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
    >>> ar.getPriority()
    '1'
    >>> ar.getPriorityText()
    u'Highest'


DateReceived field should be editable in Received state
-------------------------------------------------------

For this we need an AR with more than one Analysis:

    .. code ::

    >>> from bika.lims.adapters.widgetvisibility import DateReceivedFieldVisibility
    >>> from bika.lims.workflow import doActionFor

    >>> as2 = api.create(bika_analysisservices, 'AnalysisService', title='Another Type Of Analysis', ShortTitle='Another', Category=analysiscategory, Keyword='AN')
    >>> ar1 = create_analysisrequest(client, request, values, service_uids + [as2.UID()])

In states earlier than `sample_received` the DateReceived field is uneditable:

    .. code ::

    >>> field = ar1.getField("DateReceived")
    >>> field.checkPermission("edit", ar1) and True or False
    False

In the `sample_received` state however, it is possible to modify the field.  In this case
the SampleDateReceived adapter also simply passes the schema default unmolested.

    .. code ::

    >>> p = api.do_transition_for(ar1, 'receive')
    >>> field = ar1.getField("DateReceived")
    >>> field.checkPermission("edit", ar1) and True or False
    True

After any analysis has been submitted, the field is no longer editable.  The adapter
sets the widget.visible to 'invisible'.

    .. code ::

    >>> an = ar1.getAnalyses(full_objects=True)[0]
    >>> an.setResult('1')
    >>> p = doActionFor(an, 'submit')
    >>> DateReceivedFieldVisibility(ar1)(ar1, 'edit', ar1.schema['DateReceived'], 'default')
    'invisible'
