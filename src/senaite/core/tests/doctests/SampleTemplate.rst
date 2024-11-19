Sample Template
---------------

Running this test from the buildout directory::

    bin/test test_textual_doctests -t SampleTemplate

Needed Imports:

    >>> import re
    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.content.analysisrequest import AnalysisRequest
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils import tmpID
    >>> from bika.lims.interfaces import ISubmitted
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import getCurrentState
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from DateTime import DateTime
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from plone.app.testing import setRoles

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def get_services(sample):
    ...    analyses = sample.getAnalyses(full_objects=True)
    ...    services = map(lambda an: an.getAnalysisService(), analyses)
    ...    return services

    >>> def receive_sample(sample):
    ...     do_action_for(sample, "receive")

    >>> def submit_analyses(sample):
    ...     for analysis in sample.getAnalyses(full_objects=True):
    ...         analysis.setResult(13)
    ...         do_action_for(analysis, "submit")

    >>> def verify_analyses(sample):
    ...     for analysis in sample.getAnalyses(full_objects=True):
    ...         if ISubmitted.providedBy(analysis):
    ...             do_action_for(analysis, "verify")

    >>> def retract_analyses(sample):
    ...     for analysis in sample.getAnalyses(full_objects=True):
    ...         if ISubmitted.providedBy(analysis):
    ...             do_action_for(analysis, "retract")

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = portal.bika_setup
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Water", Prefix="W")
    >>> samplepoint = api.create(setup.samplepoints, "SamplePoint", title="Happy Lake")
    >>> container = api.create(setup.samplecontainers, "SampleContainer", title="Glass Bottle", Capacity="500ml")
    >>> preservation = api.create(setup.samplepreservations, "SamplePreservation", title=u"Chill at 4°C")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> supplier = api.create(setup.suppliers, "Supplier", Name="Naralabs")

    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())
    >>> Zn = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Zink", Keyword="Zn", Price="20", Category=category.UID())

    >>> service_uids1 = [Cu.UID(), Fe.UID(), Au.UID()]
    >>> service_uids2 = [Zn.UID()]
    >>> service_uids3 = [Cu.UID(), Fe.UID(), Au.UID(), Zn.UID()]

    >>> template1 = api.create(setup.sampletemplates, "SampleTemplate")
    >>> template1.setServices(service_uids1)

    >>> template2 = api.create(setup.sampletemplates, "SampleTemplate")
    >>> template2.setServices(service_uids2)

    >>> template3 = api.create(setup.sampletemplates, "SampleTemplate")
    >>> template3.setServices(service_uids3)


Test Template Schema and Methods
................................


Sample Point
^^^^^^^^^^^^

Templates can have a **Sample Point** assigned.

Test get/set methods:

    >>> template1.setSamplePoint(samplepoint)
    >>> template1.getSamplePoint()
    <SamplePoint at /plone/setup/samplepoints/samplepoint-1>

Test `getRaw` method:

    >>> template1.getRawSamplePoint()
    '...'

    >>> template1.getRawSamplePoint() == api.get_uid(template1.getSamplePoint())
    True

Method `getSamplePointUID` kept for backwards compatibility:

    >>> template1.getSamplePointUID() == template1.getRawSamplePoint()
    True


Sample Type
^^^^^^^^^^^

Templates can have a **Sample Type** assigned.

Test get/set methods:

    >>> template1.setSampleType(sampletype)
    >>> template1.getSampleType()
    <SampleType at /plone/setup/sampletypes/sampletype-1>

Test `getRaw` method:

    >>> template1.getRawSampleType()
    '...'

    >>> template1.getRawSampleType() == api.get_uid(template1.getSampleType())
    True


Composite
^^^^^^^^^

Templates can be marked as a **Composite**.

Test get/set methods:

    >>> template1.setComposite(True)
    >>> template1.getComposite()
    True

    >>> template1.setComposite(False)
    >>> template1.getComposite()
    False


Sampling Required
^^^^^^^^^^^^^^^^^

Templates can conditionally enable the sampling workflow.

Test get/set methods:

    >>> template1.setSamplingRequired(True)
    >>> template1.getSamplingRequired()
    True

    >>> template1.setSamplingRequired(False)
    >>> template1.getSamplingRequired()
    False


Partitions
^^^^^^^^^^

Templates can define a partition scheme for samples, which allow to set the
following fields:

    - `part_id`: A unique partition ID
    - `container`: The container used for the partition
    - `preservation`: The preservation used for the partition
    - `sampletype`: The sample type of the partition

Test get/set methods:

    >>> template1.getPartitions()
    []

    >>> partition_schema = [
    ...     {
    ...         'part_id': 'part-1',
    ...         'container': container,
    ...         'preservation': preservation,
    ...         'sampletype': sampletype,
    ...     }, {
    ...         'part_id': 'part-2',
    ...         'container': api.get_uid(container),
    ...         'preservation': api.get_uid(preservation),
    ...         'sampletype': api.get_uid(sampletype),
    ...     }
    ... ]
    >>> template1.setPartitions(partition_schema)

    >>> len(template1.getPartitions())
    2


Auto Partition
^^^^^^^^^^^^^^

Templates can be configured to automatically redirect to the partitions view on
sample reception.

Test get/set methods:

    >>> template1.setAutoPartition(True)
    >>> template1.getAutoPartition()
    True

    >>> template1.setAutoPartition(False)
    >>> template1.getAutoPartition()
    False


Services
^^^^^^^^

Analysis Services can be assigned to the Template, so that they are
automatically added when the sample is created.

Each service can be configured for a specific partition and if it should be
marked as hidden or not.


Test get/set methods:

    >>> set(template1.getServices()) == set([Cu, Fe, Au])
    True

Assign services with a list of objects

    >>> template1.setServices([api.get_uid(Cu)])
    >>> template1.getServices()
    [<AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-1>]

Assign services with a list of configuration dictionaries:

    >>> services_config = [
    ...     {
    ...         'hidden': False,
    ...         'part_id': 'part-1',
    ...         'uid': api.get_uid(Cu),
    ...     }, {
    ...         'hidden': False,
    ...         'part_id': 'part-1',
    ...         'uid': api.get_uid(Fe),
    ...     }, {
    ...         'hidden': True,
    ...         'part_id': 'part-2',
    ...         'uid': api.get_uid(Au),
    ...     }
    ... ]
    >>> template1.setServices(services_config)

    >>> set(template1.getServices()) == set([Cu, Fe, Au])
    True

Test `getRaw` method:

    >>> len(template1.getRawServices()) == len(template1.getServices())
    True

    >>> list(sorted(template1.getRawServices()[0].keys()))
    ['hidden', 'part_id', 'uid']


Get the settings for all assigned services:

    >>> template1.getAnalysisServicesSettings() == template1.getRawServices()
    True

Get the settings for a given service object/UID:

    >>> template1.getAnalysisServiceSettings(Au) == services_config[-1]
    True

Check if a specific analysis service is configured as "hidden":

    >>> template1.isAnalysisServiceHidden(Au)
    True

Get the partition ID for a given service:

    >>> template1.getAnalysisServicePartitionID(Au)
    'part-2'

    >>> template1.getAnalysisServicePartitionID(Zn)
    ''

Get the service UIDs for all assigned services:

    >>> uids = [api.get_uid(Fe), api.get_uid(Cu), api.get_uid(Au)]
    >>> all(map(lambda uid: uid in uids, template1.getServiceUIDs()))
    True

Update the settings for *all* assigned services with `setAnalysisServicesSettings` (plural):

    >>> template1.setAnalysisServicesSettings({"uid": Au, "hidden": False})

    >>> template1.isAnalysisServiceHidden(Au)
    False

Unassign a service from the template:

    >>> template1.remove_service(Au)
    True

    >>> api.get_uid(Au) in template1.getServiceUIDs()
    False

    >>> template1.remove_service(Au)
    False

Unassignment happens automatically if an Analysis Service was deactivated:

    >>> Fe in template1.getServices()
    True

    >>> api.get_uid(Fe) in template1.getServiceUIDs()
    True

    >>> api.get_uid(Fe) in template1.getRawServiceUIDs()
    True

    >>> api.get_workflow_status_of(Fe)
    'active'

    >>> success = do_action_for(Fe, "deactivate")
    >>> api.get_workflow_status_of(Fe)
    'inactive'

    >>> Fe in template1.getServices()
    False

    >>> api.get_uid(Fe) in template1.getServiceUIDs()
    False

But are kept as raw data, just in case we re-activate the service later:

    >>> Fe in template1.getServices(active_only=False)
    True

    >>> api.get_uid(Fe) in template1.getRawServiceUIDs()
    True

By default, inactive services are kept as raw data when the value is set:

    >>> template1.setServices([])
    >>> Cu in template1.getServices()
    False
    >>> Fe in template1.getServices()
    False
    >>> api.get_uid(Cu) in template1.getServiceUIDs()
    False
    >>> api.get_uid(Fe) in template1.getServiceUIDs()
    False
    >>> api.get_uid(Cu) in template1.getRawServiceUIDs()
    False
    >>> api.get_uid(Fe) in template1.getRawServiceUIDs()
    True

Unless we use `keep_inactive=False`:

    >>> template1.setServices([], keep_inactive=False)
    >>> Cu in template1.getServices()
    False
    >>> Fe in template1.getServices()
    False
    >>> api.get_uid(Cu) in template1.getServiceUIDs()
    False
    >>> api.get_uid(Fe) in template1.getServiceUIDs()
    False
    >>> api.get_uid(Cu) in template1.getRawServiceUIDs()
    False
    >>> api.get_uid(Fe) in template1.getRawServiceUIDs()
    False
