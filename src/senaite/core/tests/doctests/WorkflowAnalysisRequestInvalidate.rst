Analysis Request invalidate guard and event
===========================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowAnalysisRequestInvalidate


Test Setup
----------

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.interfaces import IAnalysisRequestRetest
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
    >>> setup = portal.bika_setup

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


Invalidate transition and guard basic constraints
-------------------------------------------------

Create an Analysis Request:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> ar
    <AnalysisRequest at /plone/clients/client-1/W-0001>

Analysis Request cannot be invalidated when the status is `sample_due`:

    >>> api.get_workflow_status_of(ar)
    'sample_due'

    >>> isTransitionAllowed(ar, "invalidate")
    False

Analysis Request cannot be invalidated when the status is `sample_received`:

    >>> success = do_action_for(ar, "receive")
    >>> api.get_workflow_status_of(ar)
    'sample_received'

    >>> isTransitionAllowed(ar, "invalidate")
    False

Submit all analyses:

    >>> for analysis in ar.getAnalyses(full_objects=True):
    ...     analysis.setResult(12)
    ...     success = do_action_for(analysis, "submit")

Analysis Request cannot be invalidated when status is `to_be_verified`:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

    >>> isTransitionAllowed(ar, "invalidate")
    False

Verify all analyses:

    >>> setup.setSelfVerificationEnabled(True)
    >>> for analysis in ar.getAnalyses(full_objects=True):
    ...     success = do_action_for(analysis, "verify")
    >>> setup.setSelfVerificationEnabled(False)

Analysis Request can be invalidated if `verified`:

    >>> api.get_workflow_status_of(ar)
    'verified'

    >>> isTransitionAllowed(ar, "invalidate")
    True

When invalidated, a retest is created:

    >>> success = do_action_for(ar, "invalidate")
    >>> api.get_workflow_status_of(ar)
    'invalid'

    >>> retest = ar.getRetest()
    >>> retest
    <AnalysisRequest at /plone/clients/client-1/W-0001-R01>

And the retest provides `IAnalysisRequestRetest` interface:

    >>> IAnalysisRequestRetest.providedBy(retest)
    True

From the retest, I can go back to the invalidated Analysis Request:

    >>> retest.getInvalidated()
    <AnalysisRequest at /plone/clients/client-1/W-0001>


Check permissions for Invalidate transition
-------------------------------------------

Create an Analysis Request, receive, submit results and verify them:

    >>> ar = new_ar([Cu])
    >>> success = do_action_for(ar, "receive")
    >>> setup.setSelfVerificationEnabled(True)
    >>> for analysis in ar.getAnalyses(full_objects=True):
    ...     analysis.setResult(12)
    ...     submitted = do_action_for(analysis, "submit")
    ...     verified = do_action_for(analysis, "verify")
    >>> setup.setSelfVerificationEnabled(False)
    >>> api.get_workflow_status_of(ar)
    'verified'

Exactly these roles can invalidate:

    >>> get_roles_for_permission("senaite.core: Transition: Invalidate", ar)
    ['LabManager', 'Manager']

Current user can assign because has the `LabManager` role:

    >>> isTransitionAllowed(ar, "invalidate")
    True

User with other roles cannot:

    >>> setRoles(portal, TEST_USER_ID, ['Analyst', 'Authenticated', 'LabClerk', 'Owner'])
    >>> isTransitionAllowed(analysis, "invalidate")
    False

Reset settings:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
