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
    <AnalysisRequest at /plone/clients/client-1/water-0001-R01>
    >>> ar.getPriority()
    '1'
    >>> ar.getPriorityText()
    u'Highest'


Proxy Fields
------------

Proxy Fields of ARs manage the getting and the setting from an equivalent field
of the underlying Sample (https://github.com/bikalabs/bika.lims/issues/1992)::

    >>> ar
    <AnalysisRequest at /plone/clients/client-1/water-0001-R01>

    >>> sample = ar.getSample()
    >>> sample
    <Sample at /plone/clients/client-1/water-0001>


DateSampled
...........

The `DateSampled` field (not to be confused with the `SamplingDate`) stores the
date of the `sample` transition, which results in the workflow state `Sampled`.
This field exists on the AR as a `ProxyField` and stores its value on the `Sample`::

    >>> ar_field = ar.getField("DateSampled")
    >>> sample_field = sample.getField("DateSampled")

    >>> ar_field
    <Field DateSampled(proxy:rw)>

    >>> sample_field
    <Field DateSampled(datetime:rw)>

The two field values should always be equal::

    >>> ar.getDateSampled() == sample.getDateSampled()
    True

Test Data::

    >>> today = DateTime()
    >>> tomorrow = DateTime() + 1

    >>> today
    DateTime('...')

    >>> tomorrow
    DateTime('...')


Setting the value on the `AnalysisRequest` proxies to the `Sample`::

    >>> ar.setDateSampled(today)

    >>> ar.getDateSampled() == today
    True

    >>> sample.getDateSampled() == today
    True

Setting the value on the `Sample` changes also the value on the `AnalysisRequest`::

    >>> sample.setDateSampled(tomorrow)

    >>> ar.getDateSampled() == tomorrow
    True

    >>> sample.getDateSampled() == tomorrow
    True


Sampler
.......

The `Sampler` is the person who took the sample. The field stores the Username
of a User within Bika LIMS who has the role of a `LabManager` or `Sampler`::

    >>> ar_field = ar.getField("Sampler")
    >>> sample_field = sample.getField("Sampler")

    >>> ar_field
    <Field Sampler(proxy:rw)>

    >>> sample_field
    <Field Sampler(string:rw)>

The two field values should always be equal::

    >>> ar.getSampler() == sample.getSampler()
    True

Test Data::

    >>> sampler1 = ploneapi.user.create(username="sampler1", password="sampler1", email="sampler1@example.com")
    >>> sampler2 = ploneapi.user.create(username="sampler2", password="sampler2", email="sampler2@example.com")

    >>> ploneapi.group.add_user(groupname="Samplers", user=sampler1)
    >>> ploneapi.group.add_user(groupname="Samplers", user=sampler2)

    >>> sampler1
    <MemberData at /plone/portal_memberdata/sampler1 used for /plone/acl_users>

    >>> sampler2
    <MemberData at /plone/portal_memberdata/sampler2 used for /plone/acl_users>

The samplers get listed now in the vocabularies of the fields::

    >>> sampler1.getId() in ar.getSamplers().keys()
    True

    >>> sampler1.getId() in sample.getSamplers().keys()
    True

    >>> sampler2.getId() in ar.getSamplers().keys()
    True

    >>> sampler2.getId() in sample.getSamplers().keys()
    True

Setting the value on the `AnalysisRequest` proxies to the `Sample`::

    >>> ar.setSampler(sampler1.getId())

    >>> ar.getSampler() == sampler1.getId()
    True

    >>> sample.getSampler() == sampler1.getId()
    True

Setting the value on the `Sample` changes also the value on the `AnalysisRequest`::

    >>> sample.setSampler(sampler2.getId())

    >>> ar.getSampler() == sampler2.getId()
    True

    >>> sample.getSampler() == sampler2.getId()
    True


ScheduledSamplingSampler
........................

The `ScheduledSamplingSampler` is the person to whom the sampling is delegated
at the schduled date. Like the `Sampler`, the field stores the Username of a
User within Bika LIMS who has the role of a `LabManager` or `Sampler`::

    >>> ar_field = ar.getField("ScheduledSamplingSampler")
    >>> sample_field = sample.getField("ScheduledSamplingSampler")

    >>> ar_field
    <Field ScheduledSamplingSampler(proxy:rw)>

    >>> sample_field
    <Field ScheduledSamplingSampler(string:rw)>

The two field values should always be equal::

    >>> ar.getScheduledSamplingSampler() == sample.getScheduledSamplingSampler()
    True

Setting the value on the `AnalysisRequest` proxies to the `Sample`::

    >>> ar.setScheduledSamplingSampler(sampler1.getId())

    >>> ar.getScheduledSamplingSampler() == sampler1.getId()
    True

    >>> sample.getScheduledSamplingSampler() == sampler1.getId()
    True

Setting the value on the `Sample` changes also the value on the `AnalysisRequest`::

    >>> sample.setScheduledSamplingSampler(sampler2.getId())

    >>> ar.getScheduledSamplingSampler() == sampler2.getId()
    True

    >>> sample.getScheduledSamplingSampler() == sampler2.getId()
    True


SamplingDate
............

The `SamplingDate` is the date when the sample was taken::

    >>> ar_field = ar.getField("SamplingDate")
    >>> sample_field = sample.getField("SamplingDate")

    >>> ar_field
    <Field SamplingDate(proxy:rw)>

    >>> sample_field
    <Field SamplingDate(datetime:rw)>

The two field values should always be equal::

    >>> ar.getSamplingDate() == sample.getSamplingDate()
    True

Test Data::

    >>> today = DateTime()
    >>> tomorrow = DateTime() + 1

    >>> today
    DateTime('...')

    >>> tomorrow
    DateTime('...')

Setting the value on the `AnalysisRequest` proxies to the `Sample`::

    >>> ar.setSamplingDate(today)

    >>> ar.getSamplingDate() == today
    True

    >>> sample.getSamplingDate() == today
    True

Setting the value on the `Sample` changes also the value on the `AnalysisRequest`::

    >>> sample.setSamplingDate(tomorrow)

    >>> ar.getSamplingDate() == tomorrow
    True

    >>> sample.getSamplingDate() == tomorrow
    True


SampleType
..........

The `SampleType` field keeps a reference to a `SampleType` object::

    >>> ar_field = ar.getField("SampleType")
    >>> sample_field = sample.getField("SampleType")

    >>> ar_field
    <Field SampleType(proxy:rw)>

    >>> sample_field
    <Field SampleType(reference:rw)>

The two field values should always be equal::

    >>> ar.getSampleType() == sample.getSampleType()
    True

Test Data::

    >>> sampletype1 = api.create(bika_sampletypes, "SampleType", Prefix="oil", MinimumVolume="100 ml")
    >>> sampletype2 = api.create(bika_sampletypes, "SampleType", Prefix="water", MinimumVolume="100 ml")

    >>> sampletype1
    <SampleType at /plone/bika_setup/bika_sampletypes/sampletype-2>

    >>> sampletype2
    <SampleType at /plone/bika_setup/bika_sampletypes/sampletype-3>

Setting the value on the `AnalysisRequest` proxies to the `Sample`::

    >>> ar.setSampleType(sampletype1)

    >>> ar.getSampleType() == sampletype1
    True

    >>> sample.getSampleType() == sampletype1
    True

Setting the value on the `Sample` changes also the value on the `AnalysisRequest`::

    >>> sample.setSampleType(sampletype2)

    >>> ar.getSampleType() == sampletype2
    True

    >>> sample.getSampleType() == sampletype2
    True

Reference fields can also handle **UID** values, so the `ProxyField` should be
able to handle this as well::

    >>> ar.setSampleType(sampletype1.UID())

    >>> ar.getSampleType() == sampletype1
    True

    >>> sample.getSampleType() == sampletype1
    True


SamplePoint
..........

The `SamplePoint` field keeps a reference to a `SamplePoint` object::

    >>> ar_field = ar.getField("SamplePoint")
    >>> sample_field = sample.getField("SamplePoint")

    >>> ar_field
    <Field SamplePoint(proxy:rw)>

    >>> sample_field
    <Field SamplePoint(reference:rw)>

The two field values should always be equal::

    >>> ar.getSamplePoint() == sample.getSamplePoint()
    True

Test Data::

    >>> samplepoint1 = api.create(bika_samplepoints, "SamplePoint", title="Bore Hole")
    >>> samplepoint2 = api.create(bika_samplepoints, "SamplePoint", title="Lake Titcaca")

    >>> samplepoint1
    <SamplePoint at /plone/bika_setup/bika_samplepoints/samplepoint-2>

    >>> samplepoint2
    <SamplePoint at /plone/bika_setup/bika_samplepoints/samplepoint-3>

Setting the value on the `AnalysisRequest` proxies to the `Sample`::

    >>> ar.setSamplePoint(samplepoint1)

    >>> ar.getSamplePoint() == samplepoint1
    True

    >>> sample.getSamplePoint() == samplepoint1
    True

Setting the value on the `Sample` changes also the value on the `AnalysisRequest`::

    >>> sample.setSamplePoint(samplepoint2)

    >>> ar.getSamplePoint() == samplepoint2
    True

    >>> sample.getSamplePoint() == samplepoint2
    True

Reference fields can also handle **UID** values, so the `ProxyField` should be
able to handle this as well::

    >>> ar.setSamplePoint(samplepoint1.UID())

    >>> ar.getSamplePoint() == samplepoint1
    True

    >>> sample.getSamplePoint() == samplepoint1
    True


StorageLocation
...............

The `StorageLocation` field keeps a reference to a `StorageLocation` object::

    >>> ar_field = ar.getField("StorageLocation")
    >>> sample_field = sample.getField("StorageLocation")

    >>> ar_field
    <Field StorageLocation(proxy:rw)>

    >>> sample_field
    <Field StorageLocation(reference:rw)>

The two field values should always be equal::

    >>> ar.getStorageLocation() == sample.getStorageLocation()
    True

Test Data::

    >>> storagelocation1 = api.create(bika_storagelocations, "StorageLocation", title="Site 1")
    >>> storagelocation2 = api.create(bika_storagelocations, "StorageLocation", title="Site 2")

    >>> storagelocation1
    <StorageLocation at /plone/bika_setup/bika_storagelocations/storagelocation-1>

    >>> storagelocation2
    <StorageLocation at /plone/bika_setup/bika_storagelocations/storagelocation-2>

Setting the value on the `AnalysisRequest` proxies to the `Sample`::

    >>> ar.setStorageLocation(storagelocation1)

    >>> ar.getStorageLocation() == storagelocation1
    True

    >>> sample.getStorageLocation() == storagelocation1
    True

Setting the value on the `Sample` changes also the value on the `AnalysisRequest`::

    >>> sample.setStorageLocation(storagelocation2)

    >>> ar.getStorageLocation() == storagelocation2
    True

    >>> sample.getStorageLocation() == storagelocation2
    True

Reference fields can also handle **UID** values, so the `ProxyField` should be
able to handle this as well::

    >>> ar.setStorageLocation(storagelocation1.UID())

    >>> ar.getStorageLocation() == storagelocation1
    True

    >>> sample.getStorageLocation() == storagelocation1
    True


ClientReference
...............

The `ClientReference` field keeps a string reference from the client::

    >>> ar_field = ar.getField("ClientReference")
    >>> sample_field = sample.getField("ClientReference")

    >>> ar_field
    <Field ClientReference(proxy:rw)>

    >>> sample_field
    <Field ClientReference(string:rw)>

The two field values should always be equal::

    >>> ar.getClientReference() == sample.getClientReference()
    True

Test Data::

    >>> clientreference1 = "Client-Reference-1"
    >>> clientreference2 = "Client-Reference-2"

Setting the value on the `AnalysisRequest` proxies to the `Sample`::

    >>> ar.setClientReference(clientreference1)

    >>> ar.getClientReference() == clientreference1
    True

    >>> sample.getClientReference() == clientreference1
    True

Setting the value on the `Sample` changes also the value on the `AnalysisRequest`::

    >>> sample.setClientReference(clientreference2)

    >>> ar.getClientReference() == clientreference2
    True

    >>> sample.getClientReference() == clientreference2
    True


ClientSampleID
...............

The `ClientSampleID` field keeps an identifier of the sample given from the client::

    >>> ar_field = ar.getField("ClientSampleID")
    >>> sample_field = sample.getField("ClientSampleID")

    >>> ar_field
    <Field ClientSampleID(proxy:rw)>

    >>> sample_field
    <Field ClientSampleID(string:rw)>

The two field values should always be equal::

    >>> ar.getClientSampleID() == sample.getClientSampleID()
    True

Test Data::

    >>> clientsampleid1 = "Client-Sample-ID-1"
    >>> clientsampleid2 = "Client-Sample-ID-2"

Setting the value on the `AnalysisRequest` proxies to the `Sample`::

    >>> ar.setClientSampleID(clientsampleid1)

    >>> ar.getClientSampleID() == clientsampleid1
    True

    >>> sample.getClientSampleID() == clientsampleid1
    True

Setting the value on the `Sample` changes also the value on the `AnalysisRequest`::

    >>> sample.setClientSampleID(clientsampleid2)

    >>> ar.getClientSampleID() == clientsampleid2
    True

    >>> sample.getClientSampleID() == clientsampleid2
    True


SamplingDeviation
.................

The `SamplingDeviation` field keeps a reference to a `SamplingDeviation` object::

    >>> ar_field = ar.getField("SamplingDeviation")
    >>> sample_field = sample.getField("SamplingDeviation")

    >>> ar_field
    <Field SamplingDeviation(proxy:rw)>

    >>> sample_field
    <Field SamplingDeviation(reference:rw)>

The two field values should always be equal::

    >>> ar.getSamplingDeviation() == sample.getSamplingDeviation()
    True

Test Data::

    >>> samplingdeviation1 = api.create(bika_samplingdeviations, "SamplingDeviation", title="Sampled by Client")
    >>> samplingdeviation2 = api.create(bika_samplingdeviations, "SamplingDeviation", title="Auto Sampled")

    >>> samplingdeviation1
    <SamplingDeviation at /plone/bika_setup/bika_samplingdeviations/samplingdeviation-1>

    >>> samplingdeviation2
    <SamplingDeviation at /plone/bika_setup/bika_samplingdeviations/samplingdeviation-2>

Setting the value on the `AnalysisRequest` proxies to the `Sample`::

    >>> ar.setSamplingDeviation(samplingdeviation1)

    >>> ar.getSamplingDeviation() == samplingdeviation1
    True

    >>> sample.getSamplingDeviation() == samplingdeviation1
    True

Setting the value on the `Sample` changes also the value on the `AnalysisRequest`::

    >>> sample.setSamplingDeviation(samplingdeviation2)

    >>> ar.getSamplingDeviation() == samplingdeviation2
    True

    >>> sample.getSamplingDeviation() == samplingdeviation2
    True

Reference fields can also handle **UID** values, so the `ProxyField` should be
able to handle this as well::

    >>> ar.setSamplingDeviation(samplingdeviation1.UID())

    >>> ar.getSamplingDeviation() == samplingdeviation1
    True

    >>> sample.getSamplingDeviation() == samplingdeviation1
    True


SampleCondition
...............

The `SampleCondition` field keeps a reference to a `SampleCondition` object::

    >>> ar_field = ar.getField("SampleCondition")
    >>> sample_field = sample.getField("SampleCondition")

    >>> ar_field
    <Field SampleCondition(proxy:rw)>

    >>> sample_field
    <Field SampleCondition(reference:rw)>

The two field values should always be equal::

    >>> ar.getSampleCondition() == sample.getSampleCondition()
    True

Test Data::

    >>> samplecondition1 = api.create(bika_sampleconditions, "SampleCondition", title="Good")
    >>> samplecondition2 = api.create(bika_sampleconditions, "SampleCondition", title="Bad")

    >>> samplecondition1
    <SampleCondition at /plone/bika_setup/bika_sampleconditions/samplecondition-1>

    >>> samplecondition2
    <SampleCondition at /plone/bika_setup/bika_sampleconditions/samplecondition-2>

Setting the value on the `AnalysisRequest` proxies to the `Sample`::

    >>> ar.setSampleCondition(samplecondition1)

    >>> ar.getSampleCondition() == samplecondition1
    True

    >>> sample.getSampleCondition() == samplecondition1
    True

Setting the value on the `Sample` changes also the value on the `AnalysisRequest`::

    >>> sample.setSampleCondition(samplecondition2)

    >>> ar.getSampleCondition() == samplecondition2
    True

    >>> sample.getSampleCondition() == samplecondition2
    True

Reference fields can also handle **UID** values, so the `ProxyField` should be
able to handle this as well::

    >>> ar.setSampleCondition(samplecondition1.UID())

    >>> ar.getSampleCondition() == samplecondition1
    True

    >>> sample.getSampleCondition() == samplecondition1
    True


EnvironmentalConditions
.......................

The `EnvironmentalConditions` field keeps a string of the environmental condition::

    >>> ar_field = ar.getField("EnvironmentalConditions")
    >>> sample_field = sample.getField("EnvironmentalConditions")

    >>> ar_field
    <Field EnvironmentalConditions(proxy:rw)>

    >>> sample_field
    <Field EnvironmentalConditions(string:rw)>

The two field values should always be equal::

    >>> ar.getEnvironmentalConditions() == sample.getEnvironmentalConditions()
    True

Test Data::

    >>> environmentalcondition1 = "Environmental-Condition-1"
    >>> environmentalcondition2 = "Environmental-Condition-2"

Setting the value on the `AnalysisRequest` proxies to the `Sample`::

    >>> ar.setEnvironmentalConditions(environmentalcondition1)

    >>> ar.getEnvironmentalConditions() == environmentalcondition1
    True

    >>> sample.getEnvironmentalConditions() == environmentalcondition1
    True

Setting the value on the `Sample` changes also the value on the `AnalysisRequest`::

    >>> sample.setEnvironmentalConditions(environmentalcondition2)

    >>> ar.getEnvironmentalConditions() == environmentalcondition2
    True

    >>> sample.getEnvironmentalConditions() == environmentalcondition2
    True


AdHoc
.....

The `AdHoc` field keeps a boolean to signal if the analysis should be done immediately::

    >>> ar_field = ar.getField("AdHoc")
    >>> sample_field = sample.getField("AdHoc")

    >>> ar_field
    <Field AdHoc(proxy:rw)>

    >>> sample_field
    <Field AdHoc(boolean:rw)>

The two field values should always be equal::

    >>> ar.getAdHoc() == sample.getAdHoc()
    True

Test Data::

    >>> adhoc1 = True
    >>> adhoc2 = False

Setting the value on the `AnalysisRequest` proxies to the `Sample`::

    >>> ar.setAdHoc(adhoc1)

    >>> ar.getAdHoc() == adhoc1
    True

    >>> sample.getAdHoc() == adhoc1
    True

Setting the value on the `Sample` changes also the value on the `AnalysisRequest`::

    >>> sample.setAdHoc(adhoc2)

    >>> ar.getAdHoc() == adhoc2
    True

    >>> sample.getAdHoc() == adhoc2
    True


Composite
.........

The `Composite` field keeps a boolean to signal if the sample is a composite::

    >>> ar_field = ar.getField("Composite")
    >>> sample_field = sample.getField("Composite")

    >>> ar_field
    <Field Composite(proxy:rw)>

    >>> sample_field
    <Field Composite(boolean:rw)>

The two field values should always be equal::

    >>> ar.getComposite() == sample.getComposite()
    True

Test Data::

    >>> composite1 = True
    >>> composite2 = False

Setting the value on the `AnalysisRequest` proxies to the `Sample`::

    >>> ar.setComposite(composite1)

    >>> ar.getComposite() == composite1
    True

    >>> sample.getComposite() == composite1
    True

Setting the value on the `Sample` changes also the value on the `AnalysisRequest`::

    >>> sample.setComposite(composite2)

    >>> ar.getComposite() == composite2
    True

    >>> sample.getComposite() == composite2
    True
