Analysis retest guard and event
===============================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowAnalysisRetest


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
    >>> setup = portal.bika_setup
    >>> date_now = DateTime().strftime("%Y-%m-%d")

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
    >>> setup.setSelfVerificationEnabled(True)

Retest transition and guard basic constraints
---------------------------------------------

Create an Analysis Request and submit results:

    >>> ar = new_ar([Cu, Fe, Au])

We cannot retest analyses if no results have been submitted yet:

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> analysis = analyses[0]
    >>> isTransitionAllowed(analysis, "retest")
    False
    >>> submit_analyses(ar)

The `retest` transition can be done now, cause the status of the analysis is
`to_be_verified`:

    >>> api.get_workflow_status_of(analysis)
    'to_be_verified'

    >>> isTransitionAllowed(analysis, "retest")
    True

When a `retest` transition is performed, a copy of the original analysis is
created (the "retest") and the original analysis is transitioned to `verified`:

    >>> analysis = analyses[0]
    >>> try_transition(analysis, "retest", "verified")
    True
    >>> api.get_workflow_status_of(analysis)
    'verified'

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> sorted(map(api.get_workflow_status_of, analyses))
    ['to_be_verified', 'to_be_verified', 'unassigned', 'verified']

Since there is one new analysis (the "retest") in `unassigned` status, the
Analysis Request is transitioned to `sample_received`:

    >>> api.get_workflow_status_of(ar)
    'sample_received'

The "retest" is a copy of original analysis:

    >>> retest = filter(lambda an: api.get_workflow_status_of(an) == "unassigned", analyses)[0]
    >>> analysis.getRetest() == retest
    True
    >>> retest.getRetestOf() == analysis
    True
    >>> retest.getKeyword() == analysis.getKeyword()
    True

But it does not keep the result:

    >>> not retest.getResult()
    True

And Result capture date is None:

    >>> not retest.getResultCaptureDate()
    True

If I submit a result for the "retest":

    >>> retest.setResult(analysis.getResult())
    >>> try_transition(retest, "submit", "to_be_verified")
    True

The status of both the analysis and the Analysis Request is "to_be_verified":

    >>> api.get_workflow_status_of(retest)
    'to_be_verified'
    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

And I can even ask for a retest of the retest:

    >>> try_transition(retest, "retest", "verified")
    True
    >>> api.get_workflow_status_of(retest)
    'verified'

A new "retest" in `unassigned` state is created and the sample rolls back to
`sample_received` status:

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> sorted(map(api.get_workflow_status_of, analyses))
    ['to_be_verified', 'to_be_verified', 'unassigned', 'verified', 'verified']
    >>> api.get_workflow_status_of(ar)
    'sample_received'

Auto-rollback of Worksheet on analysis retest
---------------------------------------------

The retesting of an analysis from a Worksheet that is in "to_be_verified" state
causes the worksheet to rollback to "open" state.

Create an Analysis Request and submit results:

    >>> ar = new_ar([Cu, Fe, Au])

Create a new Worksheet, assign all analyses and submit:

    >>> ws = api.create(portal.worksheets, "Worksheet")
    >>> for analysis in ar.getAnalyses(full_objects=True):
    ...     ws.addAnalysis(analysis)
    >>> submit_analyses(ar)

The state for both the Analysis Request and Worksheet is "to_be_verified":

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'
    >>> api.get_workflow_status_of(ws)
    'to_be_verified'

Retest one analysis:

    >>> analysis = ws.getAnalyses()[0]
    >>> try_transition(analysis, "retest", "verified")
    True

A rollback of the state of Analysis Request and Worksheet takes place:

    >>> api.get_workflow_status_of(ar)
    'sample_received'
    >>> api.get_workflow_status_of(ws)
    'open'

And both contain an additional analysis:

    >>> len(ar.getAnalyses())
    4
    >>> len(ws.getAnalyses())
    4

The state of this additional analysis, the "retest", is `assigned`:

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> retest = filter(lambda an: api.get_workflow_status_of(an) == "assigned", analyses)[0]
    >>> retest.getKeyword() == analysis.getKeyword()
    True
    >>> retest in ws.getAnalyses()
    True


Retest of an analysis with dependents
-------------------------------------

Retesting an analysis that depends on other analyses (dependents), forces the
dependents to be retested too:

Prepare a calculation that depends on `Cu` and assign it to `Fe` analysis:

    >>> calc_fe = api.create(setup.bika_calculations, 'Calculation', title='Calc for Fe')
    >>> calc_fe.setFormula("[Cu]*10")
    >>> Fe.setCalculation(calc_fe)

Prepare a calculation that depends on `Fe` and assign it to `Au` analysis:

    >>> calc_au = api.create(setup.bika_calculations, 'Calculation', title='Calc for Au')
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
    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

If I retest `Fe`, `Au` analysis is transitioned to verified and retested too:

    >>> try_transition(fe_analysis, "retest", "verified")
    True
    >>> api.get_workflow_status_of(fe_analysis)
    'verified'
    >>> api.get_workflow_status_of(au_analysis)
    'verified'

As well as `Cu` analysis, that is a dependency of `Fe`:

    >>> api.get_workflow_status_of(cu_analysis)
    'verified'

Hence, three new "retests" are generated in accordance:

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> len(analyses)
    6
    >>> au_analyses = filter(lambda an: an.getKeyword()=="Au", analyses)
    >>> sorted(map(api.get_workflow_status_of, au_analyses))
    ['unassigned', 'verified']
    >>> fe_analyses = filter(lambda an: an.getKeyword()=="Fe", analyses)
    >>> sorted(map(api.get_workflow_status_of, fe_analyses))
    ['unassigned', 'verified']
    >>> cu_analyses = filter(lambda an: an.getKeyword()=="Cu", analyses)
    >>> sorted(map(api.get_workflow_status_of, cu_analyses))
    ['unassigned', 'verified']

And the current state of the Analysis Request is `sample_received` now:

    >>> api.get_workflow_status_of(ar)
    'sample_received'


Retest of an analysis with dependencies hierarchy (recursive up)
----------------------------------------------------------------

Retesting an analysis with dependencies should end-up with retests for all them,
regardless of their position in the hierarchy of dependencies. The system works
recursively up, finding out all dependencies.

Prepare a calculation that depends on `Cu` and assign it to `Fe` analysis:

    >>> calc_fe = api.create(setup.bika_calculations, 'Calculation', title='Calc for Fe')
    >>> calc_fe.setFormula("[Cu]*10")
    >>> Fe.setCalculation(calc_fe)

Prepare a calculation that depends on `Fe` and assign it to `Au` analysis:

    >>> calc_au = api.create(setup.bika_calculations, 'Calculation', title='Calc for Au')
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
    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

If I retest `Au`, `Fe` analysis is transitioned to verified and retested too:

    >>> try_transition(au_analysis, "retest", "verified")
    True
    >>> api.get_workflow_status_of(fe_analysis)
    'verified'
    >>> api.get_workflow_status_of(au_analysis)
    'verified'

As well as `Cu` analysis, that is a dependency of `Fe`:

    >>> api.get_workflow_status_of(cu_analysis)
    'verified'

Hence, three new "retests" are generated in accordance:

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> len(analyses)
    6
    >>> au_analyses = filter(lambda an: an.getKeyword()=="Au", analyses)
    >>> sorted(map(api.get_workflow_status_of, au_analyses))
    ['unassigned', 'verified']
    >>> fe_analyses = filter(lambda an: an.getKeyword()=="Fe", analyses)
    >>> sorted(map(api.get_workflow_status_of, fe_analyses))
    ['unassigned', 'verified']
    >>> cu_analyses = filter(lambda an: an.getKeyword()=="Cu", analyses)
    >>> sorted(map(api.get_workflow_status_of, cu_analyses))
    ['unassigned', 'verified']

And the current state of the Analysis Request is `sample_received` now:

    >>> api.get_workflow_status_of(ar)
    'sample_received'


Retest of an analysis with dependents hierarchy (recursive down)
----------------------------------------------------------------

Retesting an analysis with dependents should end-up with retests for all them,
regardless of their position in the hierarchy of dependents. The system works
recursively down, finding out all dependents.

Prepare a calculation that depends on `Cu` and assign it to `Fe` analysis:

    >>> calc_fe = api.create(setup.bika_calculations, 'Calculation', title='Calc for Fe')
    >>> calc_fe.setFormula("[Cu]*10")
    >>> Fe.setCalculation(calc_fe)

Prepare a calculation that depends on `Fe` and assign it to `Au` analysis:

    >>> calc_au = api.create(setup.bika_calculations, 'Calculation', title='Calc for Au')
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
    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

If I retest `Cu`, `Fe` analysis is transitioned to verified and retested too:

    >>> try_transition(cu_analysis, "retest", "verified")
    True
    >>> api.get_workflow_status_of(cu_analysis)
    'verified'
    >>> api.get_workflow_status_of(fe_analysis)
    'verified'

As well as `Au` analysis, that is a dependent of `Fe`:

    >>> api.get_workflow_status_of(au_analysis)
    'verified'

Hence, three new "retests" are generated in accordance:

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> len(analyses)
    6
    >>> au_analyses = filter(lambda an: an.getKeyword()=="Au", analyses)
    >>> sorted(map(api.get_workflow_status_of, au_analyses))
    ['unassigned', 'verified']
    >>> fe_analyses = filter(lambda an: an.getKeyword()=="Fe", analyses)
    >>> sorted(map(api.get_workflow_status_of, fe_analyses))
    ['unassigned', 'verified']
    >>> cu_analyses = filter(lambda an: an.getKeyword()=="Cu", analyses)
    >>> sorted(map(api.get_workflow_status_of, cu_analyses))
    ['unassigned', 'verified']

And the current state of the Analysis Request is `sample_received` now:

    >>> api.get_workflow_status_of(ar)
    'sample_received'
