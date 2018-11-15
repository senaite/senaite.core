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


Retract transition and guard basic constraints
----------------------------------------------

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
