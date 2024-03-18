Analysis Request create_partitions guard and event
-------------------------------------------------

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowAnalysisRequestCreatePartitions


Test Setup
..........

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.interfaces import IAnalysisRequestRetest
    >>> from bika.lims.utils.analysis import create_analysis
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD

Functional Helpers:

    >>> def new_ar(services):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': DateTime(),
    ...         'SampleType': sampletype.UID()}
    ...     service_uids = map(api.get_uid, services)
    ...     ar = create_analysisrequest(client, request, values, service_uids)
    ...     return ar

    >>> def get_roles_for_permission(permission, context):
    ...     allowed = set(rolesForPermissionOn(permission, context))
    ...     return sorted(allowed)

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = portal.bika_setup

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


create_partitions transition and guard basic constraints
........................................................

Create an Analysis Request:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> ar
    <AnalysisRequest at /plone/clients/client-1/W-0001>

Partitions cannot be created when the status is `sample_due`:

    >>> api.get_workflow_status_of(ar)
    'sample_due'

    >>> isTransitionAllowed(ar, "create_partitions")
    False

Partitions can be created when the status is `sample_received`:

    >>> success = do_action_for(ar, "receive")
    >>> api.get_workflow_status_of(ar)
    'sample_received'

    >>> isTransitionAllowed(ar, "create_partitions")
    True

Submit all analyses:

    >>> for analysis in ar.getAnalyses(full_objects=True):
    ...     analysis.setResult(12)
    ...     success = do_action_for(analysis, "submit")

Partitions can be created when the status is `to_be_verified`:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

    >>> isTransitionAllowed(ar, "create_partitions")
    True

Verify all analyses:

    >>> bikasetup.setSelfVerificationEnabled(True)
    >>> for analysis in ar.getAnalyses(full_objects=True):
    ...     success = do_action_for(analysis, "verify")
    >>> bikasetup.setSelfVerificationEnabled(False)

Partitions can be created when the status is `verified`:

    >>> api.get_workflow_status_of(ar)
    'verified'

    >>> isTransitionAllowed(ar, "create_partitions")
    True

Partitions can be created when the status is `published`:

    >>> success = do_action_for(ar, "publish")
    >>> api.get_workflow_status_of(ar)
    'published'

    >>> isTransitionAllowed(ar, "create_partitions")
    True

Partitions cannot be created when the status is `invalid`:

    >>> success = do_action_for(ar, "invalidate")
    >>> api.get_workflow_status_of(ar)
    'invalid'

    >>> isTransitionAllowed(ar, "create_partitions")
    False

Partitions cannot be created when the status is `cancelled`:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> success = do_action_for(ar, "cancel")
    >>> api.get_workflow_status_of(ar)
    'cancelled'

    >>> isTransitionAllowed(ar, "create_partitions")
    False


Check permissions for create_partitions transition
..................................................

Create an Analysis Request and receive:

    >>> ar = new_ar([Cu])
    >>> success = do_action_for(ar, "receive")
    >>> api.get_workflow_status_of(ar)
    'sample_received'

Exactly these roles can create_partitions:

    >>> get_roles_for_permission("senaite.core: Transition: Create Partitions", ar)
    ['LabClerk', 'LabManager', 'Manager']

Current user can assign because has the `LabManager` role:

    >>> isTransitionAllowed(ar, "create_partitions")
    True

User with other roles cannot:

    >>> setRoles(portal, TEST_USER_ID, ['Analyst', 'Authenticated', 'Client', 'Owner'])
    >>> isTransitionAllowed(analysis, "create_partitions")
    False

Reset settings:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
