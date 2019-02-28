Reference Analysis (Control) verification guard and event
=========================================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowReferenceAnalysisControlVerify


Test Setup
----------

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
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
    >>> control_def = api.create(bikasetup.bika_referencedefinitions, "ReferenceDefinition", title="Control definition")
    >>> control_refs = [{'uid': api.get_uid(Cu), 'result': '10', 'min': '0', 'max': '0'},
    ...                 {'uid': api.get_uid(Fe), 'result': '10', 'min': '0', 'max': '0'},
    ...                 {'uid': api.get_uid(Au), 'result': '15', 'min': '14.5', 'max': '15.5'},]
    >>> control_def.setReferenceResults(control_refs)
    >>> control_sample = api.create(supplier, "ReferenceSample", title="Control",
    ...                      ReferenceDefinition=control_def,
    ...                      Blank=False, ExpiryDate=date_future,
    ...                      ReferenceResults=control_refs)

Control verification basic constraints
--------------------------------------

Create a Worksheet and submit regular analyses:

    >>> ar = new_ar([Cu])
    >>> worksheet = to_new_worksheet_with_reference(ar, control_sample)
    >>> submit_regular_analyses(worksheet)

Get the control and submit:

    >>> control = worksheet.getReferenceAnalyses()[0]
    >>> control.setResult(0)
    >>> try_transition(control, "submit", "to_be_verified")
    True
    >>> api.get_workflow_status_of(control)
    'to_be_verified'

I cannot verify the control because I am the same user who submitted:

    >>> try_transition(control, "verify", "verified")
    False
    >>> api.get_workflow_status_of(control)
    'to_be_verified'

And I cannot verify the Worksheet, because it can only be verified once all
analyses it contains are verified (and this is done automatically):

    >>> try_transition(worksheet, "verify", "verified")
    False
    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'

But if I enable self-verification:

    >>> bikasetup.setSelfVerificationEnabled(True)
    >>> bikasetup.getSelfVerificationEnabled()
    True

Then, I can verify my own result:

    >>> try_transition(control, "verify", "verified")
    True

And the worksheet transitions to `verified`:

    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'

And we cannot re-verify a control that has been verified already:

    >>> try_transition(control, "verify", "verified")
    False

To ensure consistency amongst tests, we disable self-verification:

    >>> bikasetup.setSelfVerificationEnabled(False)
    >>> bikasetup.getSelfVerificationEnabled()
    False


Check permissions for Verify transition
---------------------------------------

Enable self verification of results:

    >>> bikasetup.setSelfVerificationEnabled(True)
    >>> bikasetup.getSelfVerificationEnabled()
    True

Create a Worksheet and submit regular analyses:

    >>> ar = new_ar([Cu])
    >>> worksheet = to_new_worksheet_with_reference(ar, control_sample)
    >>> submit_regular_analyses(worksheet)

Get the control and submit:

    >>> control = worksheet.getReferenceAnalyses()[0]
    >>> control.setResult(12)
    >>> try_transition(control, "submit", "to_be_verified")
    True

Exactly these roles can verify:

    >>> get_roles_for_permission("senaite.core: Transition: Verify", control)
    ['LabManager', 'Manager', 'Verifier']

Current user can verify because has the `LabManager` role:

    >>> isTransitionAllowed(control, "verify")
    True

Also if the user has the roles `Manager` or `Verifier`:

    >>> setRoles(portal, TEST_USER_ID, ['Manager',])
    >>> isTransitionAllowed(control, "verify")
    True
    >>> setRoles(portal, TEST_USER_ID, ['Verifier',])
    >>> isTransitionAllowed(control, "verify")
    True

But cannot for other roles:

    >>> setRoles(portal, TEST_USER_ID, ['Analyst', 'Authenticated', 'LabClerk'])
    >>> isTransitionAllowed(control, "verify")
    False

Even if is `Owner`

    >>> setRoles(portal, TEST_USER_ID, ['Owner'])
    >>> isTransitionAllowed(control, "verify")
    False

And Clients cannot neither:

    >>> setRoles(portal, TEST_USER_ID, ['Client'])
    >>> isTransitionAllowed(control, "verify")
    False

Reset the roles for current user:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])

And to ensure consistency amongst tests, we disable self-verification:

    >>> bikasetup.setSelfVerificationEnabled(False)
    >>> bikasetup.getSelfVerificationEnabled()
    False
