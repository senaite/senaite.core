Internal Use of Samples and Analyses
====================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t InternalUse


Test Setup
----------

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.interfaces import IInternalUse
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.analysisrequest import create_partition
    >>> from bika.lims.subscribers.analysisrequest import gather_roles_for_permission
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from Products.CMFCore import permissions
    >>> from zope.lifecycleevent import modified

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

    >>> def new_sample(services, internal_use=False):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': date_now,
    ...         'SampleType': sampletype.UID(),
    ...         'InternalUse': internal_use,}
    ...     service_uids = map(api.get_uid, services)
    ...     return create_analysisrequest(client, request, values, service_uids)

    >>> def get_roles_for_permission(permission, context):
    ...     allowed = set(rolesForPermissionOn(permission, context))
    ...     return sorted(allowed)

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.bika_setup
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(setup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(setup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(setup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())


Set a Sample for internal use
-----------------------------

Create a Sample for non internal use:

    >>> sample = new_sample([Cu, Fe, Au])
    >>> transitioned = do_action_for(sample, "receive")
    >>> sample.getInternalUse()
    False
    >>> IInternalUse.providedBy(sample)
    False
    >>> internals = map(IInternalUse.providedBy, sample.getAnalyses(full_objects=True))
    >>> any(internals)
    False

Client contact does have access to this Sample:

    >>> "Owner" in gather_roles_for_permission(permissions.View, sample)
    True
    >>> "Owner" in gather_roles_for_permission(permissions.ListFolderContents, sample)
    True
    >>> "Owner" in gather_roles_for_permission(permissions.AccessContentsInformation, sample)
    True

Set the sample for internal use:

    >>> sample.setInternalUse(True)
    >>> modified(sample)
    >>> sample.getInternalUse()
    True
    >>> IInternalUse.providedBy(sample)
    True
    >>> internals = map(IInternalUse.providedBy, sample.getAnalyses(full_objects=True))
    >>> all(internals)
    True

Client contact does not have access to this Sample anymore:

    >>> "Owner" in gather_roles_for_permission(permissions.View, sample)
    False
    >>> "Owner" in gather_roles_for_permission(permissions.ListFolderContents, sample)
    False
    >>> "Owner" in gather_roles_for_permission(permissions.AccessContentsInformation, sample)
    False

Even if we submit results and sample is transitioned thereafter:

    >>> for analysis in sample.getAnalyses(full_objects=True):
    ...     analysis.setResult(12)
    ...     success = do_action_for(analysis, "submit")
    >>> api.get_workflow_status_of(sample)
    'to_be_verified'

    >>> sample.getInternalUse()
    True
    >>> IInternalUse.providedBy(sample)
    True
    >>> internals = map(IInternalUse.providedBy, sample.getAnalyses(full_objects=True))
    >>> all(internals)
    True
    >>> "Owner" in gather_roles_for_permission(permissions.View, sample)
    False
    >>> "Owner" in gather_roles_for_permission(permissions.ListFolderContents, sample)
    False
    >>> "Owner" in gather_roles_for_permission(permissions.AccessContentsInformation, sample)
    False


Creation of a Sample for internal use
-------------------------------------

Create a Sample for internal use:

    >>> sample = new_sample([Cu, Fe, Au], internal_use=True)
    >>> transitioned = do_action_for(sample, "receive")
    >>> modified(sample)
    >>> sample.getInternalUse()
    True
    >>> IInternalUse.providedBy(sample)
    True
    >>> internals = map(IInternalUse.providedBy, sample.getAnalyses(full_objects=True))
    >>> all(internals)
    True

Client contact does not have access to this Sample:

    >>> "Owner" in gather_roles_for_permission(permissions.View, sample)
    False
    >>> "Owner" in gather_roles_for_permission(permissions.ListFolderContents, sample)
    False
    >>> "Owner" in gather_roles_for_permission(permissions.AccessContentsInformation, sample)
    False


Creation of a Partition for internal use
----------------------------------------

Create a Sample for non internal use:

    >>> sample = new_sample([Cu, Fe, Au])
    >>> transitioned = do_action_for(sample, "receive")

Create two partitions, the first for internal use:

    >>> analyses = sample.getAnalyses(full_objects=True)
    >>> part1 = create_partition(sample, request, analyses[2:], internal_use=True)
    >>> part2 = create_partition(sample, request, analyses[:2], internal_use=False)
    >>> IInternalUse.providedBy(part1)
    True
    >>> IInternalUse.providedBy(part2)
    False
    >>> IInternalUse.providedBy(sample)
    False

Submit results for partition 2 (non-internal-use):

    >>> for analysis in part2.getAnalyses(full_objects=True):
    ...     analysis.setResult(12)
    ...     success = do_action_for(analysis, "submit")
    >>> api.get_workflow_status_of(part2)
    'to_be_verified'

Since partition 1 is labelled for internal use, the primary sample has been
automatically transitioned too:

    >>> api.get_workflow_status_of(sample)
    'to_be_verified'

While partition 1 remains in "received" status:

    >>> api.get_workflow_status_of(part1)
    'sample_received'
