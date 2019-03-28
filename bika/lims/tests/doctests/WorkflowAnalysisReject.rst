Analysis retract guard and event
================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowAnalysisReject


Test Setup
----------

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import getAllowedTransitions
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

    >>> def to_new_worksheet_with_duplicate(ar):
    ...     worksheet = api.create(portal.worksheets, "Worksheet")
    ...     for analysis in ar.getAnalyses(full_objects=True):
    ...         worksheet.addAnalysis(analysis)
    ...     worksheet.addDuplicateAnalyses(1)
    ...     return worksheet

    >>> def submit_regular_analyses(worksheet):
    ...     for analysis in worksheet.getRegularAnalyses():
    ...         analysis.setResult(13)
    ...         do_action_for(analysis, "submit")

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


Reject transition and guard basic constraints
---------------------------------------------

Create an Analysis Request:

    >>> ar = new_ar([Cu, Fe, Au])

Reject one of the analysis:

    >>> analysis = ar.getAnalyses(full_objects=True)[0]
    >>> try_transition(analysis, "reject", "rejected")
    True

The analysis state is now `rejected` while the AR remains in `sample_received`:

    >>> api.get_workflow_status_of(analysis)
    'rejected'
    >>> api.get_workflow_status_of(ar)
    'sample_received'

I cannot submit a result for the rejected analysis:

    >>> analysis.setResult(12)
    >>> try_transition(analysis, "submit", "to_be_verified")
    False
    >>> api.get_workflow_status_of(analysis)
    'rejected'
    >>> api.get_workflow_status_of(ar)
    'sample_received'

Submit results for the rest of the analyses:

    >>> submit_analyses(ar)

The status of the Analysis Request and its analyses is `to_be_verified`:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> sorted(map(api.get_workflow_status_of, analyses))
    ['rejected', 'to_be_verified', 'to_be_verified']

Reject one of the analyses that are in 'to_be_verified' state:

    >>> analysis = filter(lambda an: an != analysis, analyses)[0]
    >>> try_transition(analysis, "reject", "rejected")
    True
    >>> api.get_workflow_status_of(analysis)
    'rejected'

The Analysis Request remains in `to_be_verified`:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

I cannot 'reject' a verified analysis:

    >>> bikasetup.setSelfVerificationEnabled(True)
    >>> bikasetup.getSelfVerificationEnabled()
    True
    >>> analysis = filter(lambda an: api.get_workflow_status_of(an) == "to_be_verified", analyses)[0]
    >>> try_transition(analysis, "verify", "verified")
    True
    >>> try_transition(analysis, "reject", "rejected")
    False
    >>> api.get_workflow_status_of(analysis)
    'verified'
    >>> bikasetup.setSelfVerificationEnabled(False)
    >>> bikasetup.getSelfVerificationEnabled()
    False


Rejection of an analysis causes the duplicates to be removed
------------------------------------------------------------

When the analysis a duplicate comes from is rejected, the duplicate is rejected
too, regardless of its state.

Create a Worksheet and submit regular analyses:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> worksheet = to_new_worksheet_with_duplicate(ar)
    >>> submit_regular_analyses(worksheet)
    >>> api.get_workflow_status_of(ar)
    'to_be_verified'
    >>> api.get_workflow_status_of(worksheet)
    'open'

    >>> ar_ans = ar.getAnalyses(full_objects=True)
    >>> an_au = filter(lambda an: an.getKeyword() == 'Au', ar_ans)[0]
    >>> an_cu = filter(lambda an: an.getKeyword() == 'Cu', ar_ans)[0]
    >>> an_fe = filter(lambda an: an.getKeyword() == 'Fe', ar_ans)[0]
    >>> duplicates = worksheet.getDuplicateAnalyses()
    >>> du_au = filter(lambda dup: dup.getKeyword() == 'Au', duplicates)[0]
    >>> du_cu = filter(lambda dup: dup.getKeyword() == 'Cu', duplicates)[0]
    >>> du_fe = filter(lambda dup: dup.getKeyword() == 'Fe', duplicates)[0]

When the analysis `Cu` (`to_be_verified`) is rejected, the duplicate is removed:

    >>> du_cu_uid = api.get_uid(du_cu)
    >>> try_transition(an_cu, "reject", "rejected")
    True
    >>> du_cu in worksheet.getDuplicateAnalyses()
    False
    >>> api.get_object_by_uid(du_cu_uid, None) is None
    True

Submit the result for duplicate `Au` and reject `Au` analysis afterwards:

    >>> du_au_uid = api.get_uid(du_au)
    >>> du_au.setResult(12)
    >>> try_transition(du_au, "submit", "to_be_verified")
    True
    >>> api.get_workflow_status_of(du_au)
    'to_be_verified'
    >>> try_transition(an_au, "reject", "rejected")
    True
    >>> api.get_workflow_status_of(an_au)
    'rejected'
    >>> du_au in worksheet.getDuplicateAnalyses()
    False
    >>> api.get_object_by_uid(du_au_uid, None) is None
    True

Submit and verify the result for duplicate `Fe` and reject `Fe` analysis:

    >>> bikasetup.setSelfVerificationEnabled(True)
    >>> du_fe_uid = api.get_uid(du_fe)
    >>> du_fe.setResult(12)
    >>> try_transition(du_fe, "submit", "to_be_verified")
    True
    >>> try_transition(du_fe, "verify", "verified")
    True
    >>> try_transition(an_fe, "reject", "rejected")
    True
    >>> api.get_workflow_status_of(an_fe)
    'rejected'
    >>> du_fe in worksheet.getDuplicateAnalyses()
    False
    >>> api.get_object_by_uid(du_fe_uid, None) is None
    True
    >>> bikasetup.setSelfVerificationEnabled(False)


Rejection of analyses with dependents
-------------------------------------

When rejecting an analysis other analyses depends on (dependents), then the
rejection of a dependency causes the auto-rejection of its dependents.

Prepare a calculation that depends on `Cu`and assign it to `Fe` analysis:

    >>> calc_fe = api.create(bikasetup.bika_calculations, 'Calculation', title='Calc for Fe')
    >>> calc_fe.setFormula("[Cu]*10")
    >>> Fe.setCalculation(calc_fe)

Prepare a calculation that depends on `Fe` and assign it to `Au` analysis:

    >>> calc_au = api.create(bikasetup.bika_calculations, 'Calculation', title='Calc for Au')
    >>> calc_au.setFormula("([Fe])/2")
    >>> Au.setCalculation(calc_au)

Create an Analysis Request:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> cu = filter(lambda an: an.getKeyword()=="Cu", analyses)[0]
    >>> fe = filter(lambda an: an.getKeyword()=="Fe", analyses)[0]
    >>> au = filter(lambda an: an.getKeyword()=="Au", analyses)[0]

When `Fe` is rejected, `Au` analysis follows too:

    >>> try_transition(fe, "reject", "rejected")
    True
    >>> api.get_workflow_status_of(fe)
    'rejected'
    >>> api.get_workflow_status_of(au)
    'rejected'

While `Cu` analysis remains in `unassigned` state:

    >>> api.get_workflow_status_of(cu)
    'unassigned'
    >>> api.get_workflow_status_of(ar)
    'sample_received'

If we submit `Cu` and reject thereafter:

    >>> cu.setResult(12)
    >>> try_transition(cu, "submit", "to_be_verified")
    True
    >>> api.get_workflow_status_of(ar)
    'to_be_verified'
    >>> try_transition(cu, "reject", "rejected")
    True
    >>> api.get_workflow_status_of(cu)
    'rejected'

The Analysis Request rolls-back to `sample_received`:

    >>> api.get_workflow_status_of(ar)
    'sample_received'

Reset calculations:

    >>> Fe.setCalculation(None)
    >>> Au.setCalculation(None)


Effects of rejection of analysis to Analysis Request
----------------------------------------------------

Rejection of analyses have implications in the Analysis Request workflow, cause
they will not be considered anymore in regular transitions of Analysis Request
that rely on the states of its analyses.

When an Analysis is rejected, the analysis is not considered on submit:

    >>> ar = new_ar([Cu, Fe])
    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> cu = filter(lambda an: an.getKeyword() == 'Cu', analyses)[0]
    >>> fe = filter(lambda an: an.getKeyword() == 'Fe', analyses)[0]
    >>> success = do_action_for(cu, "reject")
    >>> api.get_workflow_status_of(cu)
    'rejected'
    >>> fe.setResult(12)
    >>> success = do_action_for(fe, "submit")
    >>> api.get_workflow_status_of(fe)
    'to_be_verified'
    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

Neither considered on verification:

    >>> bikasetup.setSelfVerificationEnabled(True)
    >>> success = do_action_for(fe, "verify")
    >>> api.get_workflow_status_of(fe)
    'verified'
    >>> api.get_workflow_status_of(ar)
    'verified'

Neither considered on publish:

    >>> success = do_action_for(ar, "publish")
    >>> api.get_workflow_status_of(ar)
    'published'

Reset self-verification:

    >>> bikasetup.setSelfVerificationEnabled(False)


Rejection of retests
--------------------

Create an Analysis Request, receive and submit all results:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> success = do_action_for(ar, "receive")
    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> for analysis in analyses:
    ...     analysis.setResult(12)
    ...     success = do_action_for(analysis, "submit")
    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

Retract one of the analyses:

    >>> analysis = analyses[0]
    >>> success = do_action_for(analysis, "retract")
    >>> api.get_workflow_status_of(analysis)
    'retracted'

    >>> api.get_workflow_status_of(ar)
    'sample_received'

Reject the retest:

    >>> retest = analysis.getRetest()
    >>> success = do_action_for(retest, "reject")
    >>> api.get_workflow_status_of(retest)
    'rejected'

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

Verify remaining analyses:

    >>> bikasetup.setSelfVerificationEnabled(True)
    >>> success = do_action_for(analyses[1], "verify")
    >>> success = do_action_for(analyses[2], "verify")
    >>> bikasetup.setSelfVerificationEnabled(False)

    >>> api.get_workflow_status_of(ar)
    'verified'


Check permissions for Reject transition
---------------------------------------

Create an Analysis Request:

    >>> ar = new_ar([Cu])
    >>> analysis = ar.getAnalyses(full_objects=True)[0]
    >>> allowed_roles = ['LabManager', 'Manager']
    >>> non_allowed_roles = ['Analyst', 'Authenticated', 'LabClerk', 'Owner',
    ...                      'RegulatoryInspector', 'Sampler', 'Verifier']

In unassigned state
...................

In `unassigned` state, exactly these roles can reject:

    >>> api.get_workflow_status_of(analysis)
    'unassigned'
    >>> get_roles_for_permission("Reject", analysis)
    ['LabManager', 'Manager']

Current user can reject because has the `LabManager` role:

    >>> isTransitionAllowed(analysis, "reject")
    True

Also if the user has the role `Manager`:

    >>> setRoles(portal, TEST_USER_ID, ['Manager',])
    >>> isTransitionAllowed(analysis, "reject")
    True

But cannot for other roles:

    >>> setRoles(portal, TEST_USER_ID, non_allowed_roles)
    >>> isTransitionAllowed(analysis, "reject")
    False

Reset the roles for current user:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])


In assigned state
.................

In `assigned` state, exactly these roles can reject:

    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> worksheet.addAnalysis(analysis)
    >>> api.get_workflow_status_of(analysis)
    'assigned'
    >>> get_roles_for_permission("Reject", analysis)
    ['LabManager', 'Manager']
    >>> isTransitionAllowed(analysis, "reject")
    True

Current user can reject because has the `LabManager` role:

    >>> isTransitionAllowed(analysis, "reject")
    True

Also if the user has the role `Manager`:

    >>> setRoles(portal, TEST_USER_ID, ['Manager',])
    >>> isTransitionAllowed(analysis, "reject")
    True

But cannot for other roles:

    >>> setRoles(portal, TEST_USER_ID, non_allowed_roles)
    >>> isTransitionAllowed(analysis, "reject")
    False

Reset the roles for current user:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])


In to_be_verified state
.......................

In `to_be_verified` state, exactly these roles can reject:

    >>> analysis.setResult(13)
    >>> success = do_action_for(analysis, "submit")
    >>> api.get_workflow_status_of(analysis)
    'to_be_verified'
    >>> get_roles_for_permission("Reject", analysis)
    ['LabManager', 'Manager']
    >>> isTransitionAllowed(analysis, "reject")
    True

Current user can reject because has the `LabManager` role:

    >>> isTransitionAllowed(analysis, "reject")
    True

Also if the user has the role `Manager`:

    >>> setRoles(portal, TEST_USER_ID, ['Manager',])
    >>> isTransitionAllowed(analysis, "reject")
    True

But cannot for other roles:

    >>> setRoles(portal, TEST_USER_ID, non_allowed_roles)
    >>> isTransitionAllowed(analysis, "reject")
    False

Reset the roles for current user:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])


In retracted state
..................

In `retracted` state, the analysis cannot be rejected:

    >>> success = do_action_for(analysis, "retract")
    >>> api.get_workflow_status_of(analysis)
    'retracted'
    >>> get_roles_for_permission("Reject", analysis)
    []
    >>> isTransitionAllowed(analysis, "reject")
    False


In verified state
.................

In `verified` state, the analysis cannot be rejected:

    >>> bikasetup.setSelfVerificationEnabled(True)
    >>> analysis = analysis.getRetest()
    >>> analysis.setResult(12)
    >>> success = do_action_for(analysis, "submit")
    >>> success = do_action_for(analysis, "verify")
    >>> api.get_workflow_status_of(analysis)
    'verified'
    >>> get_roles_for_permission("Reject", analysis)
    []
    >>> isTransitionAllowed(analysis, "reject")
    False


In published state
..................

In `published` state, the analysis cannot be rejected:

    >>> do_action_for(ar, "publish")
    (True, '')
    >>> api.get_workflow_status_of(analysis)
    'published'
    >>> get_roles_for_permission("Reject", analysis)
    []
    >>> isTransitionAllowed(analysis, "reject")
    False

In cancelled state
..................

In `cancelled` state, the analysis cannot be rejected:

    >>> ar = new_ar([Cu])
    >>> analysis = ar.getAnalyses(full_objects=True)[0]
    >>> success = do_action_for(ar, "cancel")
    >>> api.get_workflow_status_of(analysis)
    'cancelled'
    >>> get_roles_for_permission("Reject", analysis)
    []
    >>> isTransitionAllowed(analysis, "reject")
    False

Disable self-verification:

    >>> bikasetup.setSelfVerificationEnabled(False)


Check permissions for Rejected state
------------------------------------

In rejected state, exactly these roles can view results:

    >>> ar = new_ar([Cu])
    >>> analysis = ar.getAnalyses(full_objects=True)[0]
    >>> success = do_action_for(analysis, "reject")
    >>> api.get_workflow_status_of(analysis)
    'rejected'
    >>> get_roles_for_permission("senaite.core: View Results", analysis)
    ['LabManager', 'Manager', 'RegulatoryInspector']

And no transition can be done from this state:

    >>> getAllowedTransitions(analysis)
    []
