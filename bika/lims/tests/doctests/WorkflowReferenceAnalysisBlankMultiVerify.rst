Reference Analysis (Blank) multi-verification guard and event
=============================================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowReferenceAnalysisBlankMultiVerify


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

    >>> def to_new_worksheet_with_reference(ar, reference):
    ...     worksheet = api.create(portal.worksheets, "Worksheet")
    ...     service_uids = list()
    ...     for analysis in ar.getAnalyses(full_objects=True):
    ...         worksheet.addAnalysis(analysis)
    ...         service_uids.append(analysis.getServiceUID())
    ...     worksheet.addReferenceAnalyses(reference, service_uids)
    ...     return worksheet

    >>> def submit_regular_analyses(worksheet):
    ...     for analysis in worksheet.getRegularAnalyses():
    ...         analysis.setResult(13)
    ...         do_action_for(analysis, "submit")

    >>> def try_transition(object, transition_id, target_state_id):
    ...      success = do_action_for(object, transition_id)[0]
    ...      state = api.get_workflow_status_of(object)
    ...      return success and state == target_state_id

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
    >>> supplier = api.create(bikasetup.bika_suppliers, "Supplier", Name="Naralabs")
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())
    >>> blank_def = api.create(bikasetup.bika_referencedefinitions, "ReferenceDefinition", title="Blank definition", Blank=True)
    >>> blank_refs = [{'uid': api.get_uid(Cu), 'result': '0', 'min': '0', 'max': '0'},
    ...               {'uid': api.get_uid(Fe), 'result': '0', 'min': '0', 'max': '0'},
    ...               {'uid': api.get_uid(Au), 'result': '0', 'min': '0', 'max': '0'},]
    >>> blank_def.setReferenceResults(blank_refs)
    >>> blank_sample = api.create(supplier, "ReferenceSample", title="Blank",
    ...                    ReferenceDefinition=blank_def,
    ...                    Blank=True, ExpiryDate=date_future,
    ...                    ReferenceResults=blank_refs)

Multiverify not allowed if multi-verification is not enabled
------------------------------------------------------------

Enable self verification:

    >>> bikasetup.setSelfVerificationEnabled(True)
    >>> bikasetup.getSelfVerificationEnabled()
    True

Create a Worksheet and submit regular analyses:

    >>> ar = new_ar([Cu])
    >>> worksheet = to_new_worksheet_with_reference(ar, blank_sample)
    >>> submit_regular_analyses(worksheet)

Get the blank and submit:

    >>> blank = worksheet.getReferenceAnalyses()[0]
    >>> blank.setResult(0)
    >>> try_transition(blank, "submit", "to_be_verified")
    True

The status of blank and others is `to_be_verified`:

    >>> api.get_workflow_status_of(blank)
    'to_be_verified'
    >>> api.get_workflow_status_of(ar)
    'to_be_verified'
    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'

I cannot multi verify the blank because multi-verification is not set:

    >>> isTransitionAllowed(blank, "multi_verify")
    False
    >>> try_transition(blank, "multi_verify", "to_be_verified")
    False
    >>> api.get_workflow_status_of(blank)
    'to_be_verified'

But I can verify:

    >>> isTransitionAllowed(blank, "verify")
    True
    >>> try_transition(blank, "verify", "verified")
    True

And the status of the blank is now `verified`:

    >>> api.get_workflow_status_of(blank)
    'verified'

While the rest remain in `to_be_verified` state because the regular analysis
hasn't been verified yet:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'
    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'

To ensure consistency amongst tests, we disable self-verification:

    >>> bikasetup.setSelfVerificationEnabled(False)
    >>> bikasetup.getSelfVerificationEnabled()
    False


Multiverify transition with multi-verification enabled
------------------------------------------------------

The system allows to set multiple verifiers, both at Setup or Analysis Service
level. If set, the blank will transition to verified when the total number
of verifications equals to the value set in multiple-verifiers.

Enable self verification of results:

    >>> bikasetup.setSelfVerificationEnabled(True)
    >>> bikasetup.getSelfVerificationEnabled()
    True

Set the number of required verifications to 3:

    >>> bikasetup.setNumberOfRequiredVerifications(3)

Set the multi-verification to "Not allow same user to verify multiple times":

    >>> bikasetup.setTypeOfmultiVerification('self_multi_disabled')

Create a Worksheet and submit regular analyses:

    >>> ar = new_ar([Cu])
    >>> worksheet = to_new_worksheet_with_reference(ar, blank_sample)
    >>> submit_regular_analyses(worksheet)

Get the blank and submit:

    >>> blank = worksheet.getReferenceAnalyses()[0]
    >>> blank.setResult(12)
    >>> try_transition(blank, "submit", "to_be_verified")
    True

The status of blank and others is `to_be_verified`:

    >>> api.get_workflow_status_of(blank)
    'to_be_verified'
    >>> api.get_workflow_status_of(ar)
    'to_be_verified'
    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'

I cannot `verify`:

    >>> isTransitionAllowed(blank, "verify")
    False
    >>> try_transition(blank, "verify", "verified")
    False
    >>> api.get_workflow_status_of(blank)
    'to_be_verified'

Because multi-verification is enabled:

    >>> bikasetup.getNumberOfRequiredVerifications()
    3

And there are 3 verifications remaining:

    >>> blank.getNumberOfRemainingVerifications()
    3

But I can multi-verify:

    >>> isTransitionAllowed(blank, "multi_verify")
    True
    >>> try_transition(blank, "multi_verify", "to_be_verified")
    True

The status remains to `to_be_verified`:

    >>> api.get_workflow_status_of(blank)
    'to_be_verified'

And my user id is recorded as such:

    >>> action = getReviewHistory(blank)[0]
    >>> action['actor'] == TEST_USER_ID
    True

And now, there are two verifications remaining:

    >>> blank.getNumberOfRemainingVerifications()
    2

So, I cannot verify yet:

    >>> isTransitionAllowed(blank, "verify")
    False
    >>> try_transition(blank, "verify", "verified")
    False
    >>> api.get_workflow_status_of(blank)
    'to_be_verified'

But I cannot multi-verify neither, cause I am the same user who did the last
multi-verification:

    >>> isTransitionAllowed(blank, "multi_verify")
    False
    >>> try_transition(blank, "multi_verify", "to_be_verified")
    False
    >>> api.get_workflow_status_of(blank)
    'to_be_verified'

And the system is configured to not allow same user to verify multiple times:

    >>> bikasetup.getTypeOfmultiVerification()
    'self_multi_disabled'

But I can multi-verify if I change the type of multi-verification:

    >>> bikasetup.setTypeOfmultiVerification('self_multi_enabled')
    >>> isTransitionAllowed(blank, "multi_verify")
    True
    >>> try_transition(blank, "multi_verify", "to_be_verified")
    True

The status remains to `to_be_verified`:

    >>> api.get_workflow_status_of(blank)
    'to_be_verified'

Since there is only one verification remaining, I cannot multi-verify again:

    >>> blank.getNumberOfRemainingVerifications()
    1
    >>> isTransitionAllowed(blank, "multi_verify")
    False
    >>> try_transition(blank, "multi_verify", "to_be_verified")
    False
    >>> api.get_workflow_status_of(blank)
    'to_be_verified'

But now, I can verify:

    >>> isTransitionAllowed(blank, "verify")
    True
    >>> try_transition(blank, "verify", "verified")
    True

There is no verifications remaining:

    >>> blank.getNumberOfRemainingVerifications()
    0

And the status of the blank is now `verified`:

    >>> api.get_workflow_status_of(blank)
    'verified'

While the rest remain in `to_be_verified` state because the regular analysis
hasn't been verified yet:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'
    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'

If we multi-verify the regular analysis (2+1 times):

    >>> analysis = ar.getAnalyses(full_objects=True)[0]
    >>> try_transition(analysis, "multi_verify", "to_be_verified")
    True
    >>> try_transition(analysis, "multi_verify", "to_be_verified")
    True
    >>> try_transition(analysis, "verify", "verified")
    True

The rest transition to `to_be_verified`:

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

Create a Worksheet and submit regular analyses:

    >>> ar = new_ar([Cu])
    >>> worksheet = to_new_worksheet_with_reference(ar, blank_sample)
    >>> submit_regular_analyses(worksheet)

Get the blank and submit:

    >>> blank = worksheet.getReferenceAnalyses()[0]
    >>> blank.setResult(12)
    >>> try_transition(blank, "submit", "to_be_verified")
    True

Exactly these roles can multi_verify:

    >>> get_roles_for_permission("senaite.core: Transition: Verify", blank)
    ['LabManager', 'Manager', 'Verifier']

Current user can multi_verify because has the `LabManager` role:

    >>> isTransitionAllowed(blank, "multi_verify")
    True

Also if the user has the roles `Manager` or `Verifier`:

    >>> setRoles(portal, TEST_USER_ID, ['Manager',])
    >>> isTransitionAllowed(blank, "multi_verify")
    True
    >>> setRoles(portal, TEST_USER_ID, ['Verifier',])
    >>> isTransitionAllowed(blank, "multi_verify")
    True

But cannot for other roles:

    >>> setRoles(portal, TEST_USER_ID, ['Analyst', 'Authenticated', 'LabClerk'])
    >>> isTransitionAllowed(blank, "multi_verify")
    False

Even if is `Owner`

    >>> setRoles(portal, TEST_USER_ID, ['Owner'])
    >>> isTransitionAllowed(blank, "multi_verify")
    False

And Clients cannot neither:

    >>> setRoles(portal, TEST_USER_ID, ['Client'])
    >>> isTransitionAllowed(blank, "multi_verify")
    False

Reset the roles for current user:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])

And to ensure consistency amongst tests, we disable self-verification:

    >>> bikasetup.setSelfVerificationEnabled(False)
    >>> bikasetup.getSelfVerificationEnabled()
    False
