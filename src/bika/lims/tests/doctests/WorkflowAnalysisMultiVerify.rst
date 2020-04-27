Analysis multi-verification guard and event
===========================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowAnalysisMultiVerify


Test Setup
----------

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import getReviewHistory
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD

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

    >>> def new_ar(services):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': date_now,
    ...         'SampleType': sampletype.UID()}
    ...     service_uids = map(api.get_uid, services)
    ...     ar = create_analysisrequest(client, request, values, service_uids)
    ...     transitioned = do_action_for(ar, "receive")
    ...     return ar

    >>> def try_transition(object, transition_id, target_state_id):
    ...      success = do_action_for(object, transition_id)[0]
    ...      state = api.get_workflow_status_of(object)
    ...      return success and state == target_state_id

    >>> def submit_analyses(ar):
    ...     for analysis in ar.getAnalyses(full_objects=True):
    ...         analysis.setResult(13)
    ...         do_action_for(analysis, "submit")

    >>> def get_roles_for_permission(permission, context):
    ...     allowed = set(rolesForPermissionOn(permission, context))
    ...     return sorted(allowed)


Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> bikasetup = portal.bika_setup
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(bikasetup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(bikasetup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(bikasetup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())


Multiverify not allowed if multi-verification is not enabled
------------------------------------------------------------

Enable the self verification:

    >>> bikasetup.setSelfVerificationEnabled(True)
    >>> bikasetup.getSelfVerificationEnabled()
    True

Create an Analysis Request and submit results:

    >>> ar = new_ar([Cu])
    >>> submit_analyses(ar)

The status of the Analysis Request and its analyses is `to_be_verified`:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> analysis = analyses[0]
    >>> api.get_workflow_status_of(analysis)
    'to_be_verified'

I cannot multi verify the analysis because multi-verification is not set:

    >>> isTransitionAllowed(analysis, "multi_verify")
    False
    >>> try_transition(analysis, "multi_verify", "to_be_verified")
    False
    >>> api.get_workflow_status_of(analysis)
    'to_be_verified'

But I can verify:

    >>> isTransitionAllowed(analysis, "verify")
    True
    >>> try_transition(analysis, "verify", "verified")
    True

And the status of the analysis and others is now `verified`:

    >>> api.get_workflow_status_of(analysis)
    'verified'
    >>> api.get_workflow_status_of(ar)
    'verified'

To ensure consistency amongst tests, we disable self-verification:

    >>> bikasetup.setSelfVerificationEnabled(False)
    >>> bikasetup.getSelfVerificationEnabled()
    False


Multiverify transition with multi-verification enabled
------------------------------------------------------

The system allows to set multiple verifiers, both at Setup or Analysis Service
level. If set, the analysis will transition to verified when the total number
of verifications equals to the value set in multiple-verifiers.

Enable self verification of results:

    >>> bikasetup.setSelfVerificationEnabled(True)
    >>> bikasetup.getSelfVerificationEnabled()
    True

Set the number of required verifications to 3:

    >>> bikasetup.setNumberOfRequiredVerifications(3)

Set the multi-verification to "Not allow same user to verify multiple times":

    >>> bikasetup.setTypeOfmultiVerification('self_multi_disabled')

Create an Analysis Request, a worksheet and submit results:

    >>> ar = new_ar([Cu])
    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> for analysis in ar.getAnalyses(full_objects=True):
    ...     worksheet.addAnalysis(analysis)
    >>> submit_analyses(ar)

The status of the Analysis Request, the Worksheet and analyses is
`to_be_verified`:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'
    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'
    >>> analysis = ar.getAnalyses(full_objects=True)[0]
    >>> api.get_workflow_status_of(analysis)
    'to_be_verified'

I cannot `verify`:

    >>> isTransitionAllowed(analysis, "verify")
    False
    >>> try_transition(analysis, "verify", "verified")
    False
    >>> api.get_workflow_status_of(analysis)
    'to_be_verified'

Because multi-verification is enabled:

    >>> bikasetup.getNumberOfRequiredVerifications()
    3

And there are 3 verifications remaining:

    >>> analysis.getNumberOfRemainingVerifications()
    3

But I can multi-verify:

    >>> isTransitionAllowed(analysis, "multi_verify")
    True
    >>> try_transition(analysis, "multi_verify", "to_be_verified")
    True

The status of the analysis and others is still `to_be_verified`:

    >>> api.get_workflow_status_of(analysis)
    'to_be_verified'
    >>> api.get_workflow_status_of(ar)
    'to_be_verified'
    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'

And my user id is recorded as such:

    >>> action = getReviewHistory(analysis)[0]
    >>> action['actor'] == TEST_USER_ID
    True

And now, there are two verifications remaining:

    >>> analysis.getNumberOfRemainingVerifications()
    2

So, I cannot verify yet:

    >>> isTransitionAllowed(analysis, "verify")
    False
    >>> try_transition(analysis, "verify", "verified")
    False
    >>> api.get_workflow_status_of(analysis)
    'to_be_verified'

But I cannot multi-verify neither, cause I am the same user who did the last
multi-verification:

    >>> isTransitionAllowed(analysis, "multi_verify")
    False
    >>> try_transition(analysis, "multi_verify", "to_be_verified")
    False
    >>> api.get_workflow_status_of(analysis)
    'to_be_verified'

And the system is configured to not allow same user to verify multiple times:

    >>> bikasetup.getTypeOfmultiVerification()
    'self_multi_disabled'

But I can multi-verify if I change the type of multi-verification:

    >>> bikasetup.setTypeOfmultiVerification('self_multi_enabled')
    >>> isTransitionAllowed(analysis, "multi_verify")
    True
    >>> try_transition(analysis, "multi_verify", "to_be_verified")
    True

The status of the analysis and others is still `to_be_verified`:

    >>> api.get_workflow_status_of(analysis)
    'to_be_verified'
    >>> api.get_workflow_status_of(ar)
    'to_be_verified'
    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'

And now, there is only verifications remaining:

    >>> analysis.getNumberOfRemainingVerifications()
    1

Since there is only one verification remaining, I cannot multi-verify again:

    >>> isTransitionAllowed(analysis, "multi_verify")
    False
    >>> try_transition(analysis, "multi_verify", "to_be_verified")
    False
    >>> api.get_workflow_status_of(analysis)
    'to_be_verified'

But now, I can verify:

    >>> isTransitionAllowed(analysis, "verify")
    True
    >>> try_transition(analysis, "verify", "verified")
    True

There is no verifications remaining:

    >>> analysis.getNumberOfRemainingVerifications()
    0

And the status of the analysis and others is now `verified`:

    >>> api.get_workflow_status_of(analysis)
    'verified'
    >>> api.get_workflow_status_of(ar)
    'verified'
    >>> api.get_workflow_status_of(worksheet)
    'verified'

To ensure consistency amongst tests, we disable self-verification:

    >>> bikasetup.setSelfVerificationEnabled(False)
    >>> bikasetup.getSelfVerificationEnabled()
    False


Check permissions for Multi verify transition
---------------------------------------------

Enable self verification of results:

    >>> bikasetup.setSelfVerificationEnabled(True)
    >>> bikasetup.getSelfVerificationEnabled()
    True

Set the number of required verifications to 3:

    >>> bikasetup.setNumberOfRequiredVerifications(3)

Set the multi-verification to "Allow same user to verify multiple times":

    >>> bikasetup.setTypeOfmultiVerification('self_multi_enabled')

Create an Analysis Request and submit results:

    >>> ar = new_ar([Cu])
    >>> submit_analyses(ar)

The status of the Analysis Request and its analyses is `to_be_verified`:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> map(api.get_workflow_status_of, analyses)
    ['to_be_verified']

Exactly these roles can multi-verify:

    >>> analysis = analyses[0]
    >>> get_roles_for_permission("senaite.core: Transition: Verify", analysis)
    ['LabManager', 'Manager', 'Verifier']

Current user can multi-verify because has the `LabManager` role:

    >>> isTransitionAllowed(analysis, "multi_verify")
    True

Also if the user has the roles `Manager` or `Verifier`:

    >>> setRoles(portal, TEST_USER_ID, ['Manager',])
    >>> isTransitionAllowed(analysis, "multi_verify")
    True
    >>> setRoles(portal, TEST_USER_ID, ['Verifier',])
    >>> isTransitionAllowed(analysis, "multi_verify")
    True

But cannot for other roles:

    >>> setRoles(portal, TEST_USER_ID, ['Analyst', 'Authenticated', 'LabClerk'])
    >>> isTransitionAllowed(analysis, "multi_verify")
    False

Even if is `Owner`

    >>> setRoles(portal, TEST_USER_ID, ['Owner'])
    >>> isTransitionAllowed(analysis, "multi_verify")
    False

And Clients cannot neither:

    >>> setRoles(portal, TEST_USER_ID, ['Client'])
    >>> isTransitionAllowed(analysis, "multi_verify")
    False

Reset the roles for current user:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])

And to ensure consistency amongst tests, we disable self-verification:

    >>> bikasetup.setSelfVerificationEnabled(False)
    >>> bikasetup.getSelfVerificationEnabled()
    False
