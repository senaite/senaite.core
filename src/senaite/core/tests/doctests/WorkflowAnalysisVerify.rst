Analysis verification guard and event
=====================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowAnalysisVerify


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


Verify transition and guard basic constraints
---------------------------------------------

Create an Analysis Request and submit results:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> submit_analyses(ar)

The status of the Analysis Request and its analyses is `to_be_verified`:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> map(api.get_workflow_status_of, analyses)
    ['to_be_verified', 'to_be_verified', 'to_be_verified']

I cannot verify the analyses because I am the same user who submitted them:

    >>> try_transition(analyses[0], "verify", "verified")
    False
    >>> api.get_workflow_status_of(analyses[0])
    'to_be_verified'

    >>> try_transition(analyses[1], "verify", "verified")
    False
    >>> api.get_workflow_status_of(analyses[1])
    'to_be_verified'

    >>> try_transition(analyses[2], "verify", "verified")
    False
    >>> api.get_workflow_status_of(analyses[2])
    'to_be_verified'

And I cannot verify Analysis Request neither, because the Analysis Request can
only be verified once all the analyses it contains are verified (and this is
done automatically):

    >>> try_transition(ar, "verify", "verified")
    False
    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

But if enable the self verification:

    >>> bikasetup.setSelfVerificationEnabled(True)
    >>> bikasetup.getSelfVerificationEnabled()
    True

Then, I will be able to verify my own results:

    >>> try_transition(analyses[0], "verify", "verified")
    True
    >>> try_transition(analyses[1], "verify", "verified")
    True

But the Analysis Request will remain in `to_be_verified` state:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

Until we verify all the analyses it contains:

    >>> try_transition(analyses[2], "verify", "verified")
    True
    >>> api.get_workflow_status_of(ar)
    'verified'

And we cannot re-verify an analysis that has been verified already:

    >>> try_transition(analyses[2], "verify", "verified")
    False

To ensure consistency amongst tests, we disable self-verification:

    >>> bikasetup.setSelfVerificationEnabled(False)
    >>> bikasetup.getSelfVerificationEnabled()
    False


Auto verification of Worksheets when all its analyses are verified
------------------------------------------------------------------

The same behavior as for Analysis Requests applies to the worksheet when all its
analyses are verified.

Enable self verification of results:

    >>> bikasetup.setSelfVerificationEnabled(True)
    >>> bikasetup.getSelfVerificationEnabled()
    True

Create two Analysis Requests:

    >>> ar0 = new_ar([Cu, Fe, Au])
    >>> ar1 = new_ar([Cu, Fe])

Create a worksheet:

    >>> worksheet = api.create(portal.worksheets, "Worksheet")

And assign all the analyses from the Analysis Requests created before, except
`Au` from the first Analysis Request:

    >>> analyses_ar0 = ar0.getAnalyses(full_objects=True)
    >>> analyses_ar1 = ar1.getAnalyses(full_objects=True)
    >>> analyses = filter(lambda an: an.getKeyword() != 'Au', analyses_ar0)
    >>> analyses += analyses_ar1
    >>> for analysis in analyses:
    ...     worksheet.addAnalysis(analysis)

And submit results for all analyses:

    >>> submit_analyses(ar0)
    >>> submit_analyses(ar1)

Of course I cannot verify the whole worksheet, because a worksheet can only be
verified once all the analyses it contains are in verified state (and this is
done automatically):

    >>> try_transition(worksheet, "verify", "verified")
    False

And verify all analyses from worksheet except one:

    >>> ws_analyses = worksheet.getAnalyses()
    >>> analysis_1 = analyses[0]
    >>> analysis_2 = analyses[1]
    >>> analysis_3 = analyses[2]
    >>> analysis_4 = analyses[3]

    >>> try_transition(analysis_2, "verify", "verified")
    True
    >>> try_transition(analysis_3, "verify", "verified")
    True
    >>> try_transition(analysis_4, "verify", "verified")
    True

The Analysis Request number 1 has been automatically transitioned to `verified`
cause all the contained analyses have been verified:

    >>> api.get_workflow_status_of(ar1)
    'verified'

While Analysis Request number 0 has not been transitioned because have two
analyses to be verifed still:

    >>> api.get_workflow_status_of(ar0)
    'to_be_verified'

And same with worksheet, cause there is one analysis pending:

    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'

And again, I cannot verify the whole worksheet by myself, because a worksheet
can only be verified once all the analyses it contains are in verified state
(and this is done automatically):

    >>> try_transition(worksheet, "verify", "verified")
    False

If we verify the pending analysis from the worksheet:

    >>> try_transition(analysis_1, "verify", "verified")
    True

The worksheet will follow:

    >>> api.get_workflow_status_of(worksheet)
    'verified'

But the Analysis Request number 0 will remain in `to_be_verified` state:

    >>> api.get_workflow_status_of(ar0)
    'to_be_verified'

Unless we verify the analysis `Au`:

    >>> au_an = filter(lambda an: an.getKeyword() == 'Au', analyses_ar0)[0]
    >>> try_transition(au_an, "verify", "verified")
    True

    >>> api.get_workflow_status_of(ar0)
    'verified'


Verification of results for analyses with dependencies
------------------------------------------------------

If an analysis is associated to a calculation that uses the result of other
analyses (dependents), then the verification of a dependency will auto-verify
its dependents.

Reset the interim fields for analysis `Au`:

    >>> Au.setInterimFields([])

Prepare a calculation that depends on `Cu` and assign it to `Fe` analysis:

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
    >>> cu_analysis = filter(lambda an: an.getKeyword()=="Cu", analyses)[0]
    >>> fe_analysis = filter(lambda an: an.getKeyword()=="Fe", analyses)[0]
    >>> au_analysis = filter(lambda an: an.getKeyword()=="Au", analyses)[0]

TODO This should not be like this, but the calculation is performed by
`ajaxCalculateAnalysisEntry`. The calculation logic must be moved to
'api.analysis.calculate`:

    >>> cu_analysis.setResult(20)
    >>> fe_analysis.setResult(12)
    >>> au_analysis.setResult(10)

Submit `Au` analysis and the rest will follow:

    >>> try_transition(au_analysis, "submit", "to_be_verified")
    True
    >>> api.get_workflow_status_of(au_analysis)
    'to_be_verified'
    >>> api.get_workflow_status_of(fe_analysis)
    'to_be_verified'
    >>> api.get_workflow_status_of(cu_analysis)
    'to_be_verified'

If I verify `Au`, the rest of analyses (dependents) will follow too:

    >>> try_transition(au_analysis, "verify", "verified")
    True
    >>> api.get_workflow_status_of(au_analysis)
    'verified'
    >>> api.get_workflow_status_of(fe_analysis)
    'verified'
    >>> api.get_workflow_status_of(cu_analysis)
    'verified'

And Analysis Request is transitioned too:

    >>> api.get_workflow_status_of(ar)
    'verified'

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

Create an Analysis Request and submit results:

    >>> ar = new_ar([Cu])
    >>> submit_analyses(ar)

The status of the Analysis Request and its analyses is `to_be_verified`:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> map(api.get_workflow_status_of, analyses)
    ['to_be_verified']

Exactly these roles can verify:

    >>> analysis = analyses[0]
    >>> get_roles_for_permission("senaite.core: Transition: Verify", analysis)
    ['LabManager', 'Manager', 'Verifier']

Current user can verify because has the `LabManager` role:

    >>> isTransitionAllowed(analysis, "verify")
    True

Also if the user has the roles `Manager` or `Verifier`:

    >>> setRoles(portal, TEST_USER_ID, ['Manager',])
    >>> isTransitionAllowed(analysis, "verify")
    True
    >>> setRoles(portal, TEST_USER_ID, ['Verifier',])
    >>> isTransitionAllowed(analysis, "verify")
    True

But cannot for other roles:

    >>> setRoles(portal, TEST_USER_ID, ['Analyst', 'Authenticated', 'LabClerk'])
    >>> isTransitionAllowed(analysis, "verify")
    False

Even if is `Owner`

    >>> setRoles(portal, TEST_USER_ID, ['Owner'])
    >>> isTransitionAllowed(analysis, "verify")
    False

And Clients cannot neither:

    >>> setRoles(portal, TEST_USER_ID, ['Client'])
    >>> isTransitionAllowed(analysis, "verify")
    False

Reset the roles for current user:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])

And to ensure consistency amongst tests, we disable self-verification:

    >>> bikasetup.setSelfVerificationEnabled(False)
    >>> bikasetup.getSelfVerificationEnabled()
    False
