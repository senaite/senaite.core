Analysis Profile
----------------

Running this test from the buildout directory::

    bin/test test_textual_doctests -t AnalysisProfile

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
    >>> setup = portal.setup
    >>> bikasetup = portal.bika_setup
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Water", Prefix="W")
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
    >>> profile1 = api.create(setup.analysisprofiles, "AnalysisProfile")
    >>> profile1.setServices(service_uids1)
    >>> profile2 = api.create(setup.analysisprofiles, "AnalysisProfile")
    >>> profile2.setServices(service_uids2)
    >>> profile3 = api.create(setup.analysisprofiles, "AnalysisProfile")
    >>> profile3.setServices(service_uids3)


Test Profile Price, VAT and calcluations
........................................

    >>> profile1.setAnalysisProfilePrice(200)
    >>> profile1.setAnalysisProfileVAT(19)
    >>> profile1.getVATAmount()
    38.0
    >>> profile1.getTotalPrice()
    238.0


Assign Profile(s)
.................

Assigning Analysis Profiles adds the Analyses of the profile to the sample.

    >>> bikasetup.setSelfVerificationEnabled(True)

    >>> values = {
    ...     'Client': client.UID(),
    ...     'Contact': contact.UID(),
    ...     'DateSampled': date_now,
    ...     'SampleType': sampletype.UID()}

Create some Analysis Requests:

    >>> ar1 = create_analysisrequest(client, request, values, [Au.UID()])
    >>> ar2 = create_analysisrequest(client, request, values, [Fe.UID()])
    >>> ar3 = create_analysisrequest(client, request, values, [Cu.UID()])

Apply the profile object. Note the custom `setProfiles` (plural) setter:

    >>> ar1.setProfiles(profile1)

All analyses from the profile should be added to the sample:

   >>> services = get_services(ar1)
   >>> set(map(api.get_uid, services)).issuperset(service_uids1)
   True

The profile is applied to the sample:

   >>> profile1 in ar1.getProfiles()
   True
   
Apply the profile UID:

    >>> ar2.setProfiles(profile2.UID())

All analyses from the profile should be added to the sample:

   >>> services = get_services(ar2)
   >>> set(map(api.get_uid, services)).issuperset(service_uids2)
   True

The profile is applied to the sample:

   >>> profile2 in ar2.getProfiles()
   True


Apply multiple profiles:

    >>> ar3.setProfiles([profile1, profile2, profile3.UID()])

All analyses from the profiles should be added to the sample:

   >>> services = get_services(ar3)
   >>> set(map(api.get_uid, services)).issuperset(service_uids1 + service_uids2 + service_uids3)
   True


Remove Profile(s)
.................

Removing an analyis Sample retains the assigned analyses:

    >>> analyses = ar1.getAnalyses(full_objects=True)
    >>> ar1.setProfiles([])
    >>> ar1.getProfiles()
    []

   >>> set(ar1.getAnalyses(full_objects=True)) == set(analyses)
   True


Assigning Profiles in "to_be_verified" status
.............................................

    >>> ar4 = create_analysisrequest(client, request, values, [Au.UID()])

    >>> receive_sample(ar4)
    >>> submit_analyses(ar4)

    >>> api.get_workflow_status_of(ar4)
    'to_be_verified'

    >>> ar4.getProfiles()
    []

Setting the profile works up to this state:

    >>> ar4.setProfiles(profile1.UID())
    >>> api.get_workflow_status_of(ar4)
    'sample_received'

    >>> services = get_services(ar3)
    >>> set(map(api.get_uid, services)).issuperset(service_uids1 + [Au.UID()])
    True


Inactive services
.................

Inactive services are not returned by default:

    >>> Fe in profile1.getServices()
    True

    >>> success = do_action_for(Fe, "deactivate")
    >>> api.get_workflow_status_of(Fe)
    'inactive'

    >>> Fe in profile1.getServices()
    False

But kept as raw data, just in case we re-activate the service later:

    >>> Fe in profile1.getServices(active_only=False)
    True

    >>> api.get_uid(Fe) in profile1.getRawServiceUIDs()
    True

By default, inactive services are kept as raw data when the value is set:

    >>> profile1.setServices([])
    >>> Cu in profile1.getServices()
    False
    >>> Fe in profile1.getServices()
    False
    >>> api.get_uid(Cu) in profile1.getServiceUIDs()
    False
    >>> api.get_uid(Fe) in profile1.getServiceUIDs()
    False
    >>> api.get_uid(Cu) in profile1.getRawServiceUIDs()
    False
    >>> api.get_uid(Fe) in profile1.getRawServiceUIDs()
    True

Unless we use `keep_inactive=False`:

    >>> profile1.setServices([], keep_inactive=False)
    >>> Cu in profile1.getServices()
    False
    >>> Fe in profile1.getServices()
    False
    >>> api.get_uid(Cu) in profile1.getServiceUIDs()
    False
    >>> api.get_uid(Fe) in profile1.getServiceUIDs()
    False
    >>> api.get_uid(Cu) in profile1.getRawServiceUIDs()
    False
    >>> api.get_uid(Fe) in profile1.getRawServiceUIDs()
    False
