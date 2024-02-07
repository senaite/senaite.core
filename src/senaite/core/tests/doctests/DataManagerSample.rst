Sample Data Manager
-------------------

A data manager is an object adapter to get/set/query data by a name.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t DataManagerSample


Test Setup
..........

Needed Imports:

    >>> from operator import methodcaller
    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from DateTime import DateTime
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.analysisrequest import create_partition
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from plone.app.testing import setRoles

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def new_sample(services, client, contact, sample_type, date_sampled=None):
    ...     values = {
    ...         'Client': api.get_uid(client),
    ...         'Contact': api.get_uid(contact),
    ...         'DateSampled': date_sampled or DateTime().strftime("%Y-%m-%d"),
    ...         'SampleType': api.get_uid(sample_type),
    ...     }
    ...     service_uids = map(api.get_uid, services)
    ...     sample = create_analysisrequest(client, request, values, service_uids)
    ...     return sample

    >>> def get_analysis_from(sample, service):
    ...     service_uid = api.get_uid(service)
    ...     for analysis in sample.getAnalyses(full_objects=True):
    ...         if analysis.getServiceUID() == service_uid:
    ...             return analysis
    ...     return None

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = api.get_bika_setup()

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(bikasetup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(bikasetup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())


Using the data manager to set sample values
...........................................

Create a new sample:

    >>> sample = new_sample([Cu, Fe, Au], client, contact, sampletype)
    >>> api.get_workflow_status_of(sample)
    'sample_due'

Receive the sample:

    >>> transitioned = do_action_for(sample, "receive")
    >>> api.get_workflow_status_of(sample)
    'sample_received'

Get the data manager:

    >>> from senaite.core.interfaces import IDataManager

    >>> dm =  IDataManager(sample)
    >>> dm
    <senaite.core.datamanagers.sample.SampleDataManager object at 0x...>

Set a text field:

    >>> dm.set("EnvironmentalConditions", "sunny")
    [<AnalysisRequest at /plone/clients/client-1/W-0001>]

    >>> dm.get("EnvironmentalConditions")
    'sunny'

Set a bool field:

    >>> dm.set("Composite", True)
    [<AnalysisRequest at /plone/clients/client-1/W-0001>]

    >>> dm.get("Composite")
    True

Set a reference field:

    >>> dm.set("CCContact", [contact])
    [<AnalysisRequest at /plone/clients/client-1/W-0001>]

    >>> dm.get("CCContact")
    [<Contact at /plone/clients/client-1/contact-1>]


Set a date field:

    >>> dm.set("DateSampled", "2000-12-31")
    [<AnalysisRequest at /plone/clients/client-1/W-0001>]

    >>> dm.get("DateSampled").strftime("%Y-%m-%d")
    '2000-12-31'
