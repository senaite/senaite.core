Analysis submission guard and event
===================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowAnalysisSubmit


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

    >>> setRoles(portal, TEST_USER_ID, ['LabManager', 'Sampler'])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(bikasetup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(bikasetup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(bikasetup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())


Basic constraints for Analysis submission
-----------------------------------------

Create an Analysis Request:

    >>> values = {'Client': client.UID(),
    ...           'Contact': contact.UID(),
    ...           'DateSampled': date_now,
    ...           'SampleType': sampletype.UID()}
    >>> service_uids = map(api.get_uid, [Cu])
    >>> ar = create_analysisrequest(client, request, values, service_uids)

Cannot submit if the Analysis Request has not been yet received:

    >>> analysis = ar.getAnalyses(full_objects=True)[0]
    >>> analysis.setResult(12)
    >>> isTransitionAllowed(analysis, "submit")
    False
    >>> transitioned = do_action_for(analysis, "submit")
    >>> transitioned[0]
    False
    >>> api.get_workflow_status_of(analysis)
    'registered'

But if I receive the Analysis Request:

    >>> transitioned = do_action_for(ar, "receive")
    >>> transitioned[0]
    True
    >>> api.get_workflow_status_of(ar)
    'sample_received'

I can then submit the analysis:

    >>> transitioned = do_action_for(analysis, "submit")
    >>> transitioned[0]
    True
    >>> api.get_workflow_status_of(analysis)
    'to_be_verified'

And I cannot resubmit the analysis:

    >>> isTransitionAllowed(analysis, "submit")
    False
    >>> transitioned = do_action_for(analysis, "submit")
    >>> transitioned[0]
    False
    >>> api.get_workflow_status_of(analysis)
    'to_be_verified'


Basic constraints for "field" Analysis submission
-------------------------------------------------

Set analysis `Cu` with Point of Capture "field":

    >>> Cu.setPointOfCapture("field")
    >>> Cu.getPointOfCapture()
    'field'

And activate sampling workflow:

    >>> bikasetup.setSamplingWorkflowEnabled(True)
    >>> bikasetup.getSamplingWorkflowEnabled()
    True

Create an Analysis Request:

    >>> values = {'Client': client.UID(),
    ...           'Contact': contact.UID(),
    ...           'SampleType': sampletype.UID()}
    >>> service_uids = map(api.get_uid, [Cu, Fe])
    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> cu = filter(lambda an: an.getKeyword() == "Cu", analyses)[0]
    >>> fe = filter(lambda an: an.getKeyword() == "Fe", analyses)[0]

Cannot submit `Cu`, because the Analysis Request has not been yet sampled:

    >>> cu.setResult(12)
    >>> isTransitionAllowed(cu, "submit")
    False
    >>> api.get_workflow_status_of(ar)
    'to_be_sampled'

I cannot submit `Fe` neither, cause the Analysis Request has not been received:

    >>> fe.setResult(12)
    >>> isTransitionAllowed(fe, "submit")
    False

If I sample the Analysis Request:

    >>> ar.setDateSampled(timestamp())
    >>> ar.setSampler(TEST_USER_ID)
    >>> transitioned = do_action_for(ar, "sample")
    >>> transitioned[0]
    True
    >>> api.get_workflow_status_of(ar)
    'sample_due'

Then I can submit `Cu`:

    >>> transitioned = do_action_for(cu, "submit")
    >>> transitioned[0]
    True
    >>> api.get_workflow_status_of(cu)
    'to_be_verified'

But cannot submit `Fe`:

    >>> cu.setResult(12)
    >>> isTransitionAllowed(fe, "submit")
    False

Unless I receive the Analysis Request:

    >>> transitioned = do_action_for(ar, "receive")
    >>> transitioned[0]
    True
    >>> api.get_workflow_status_of(ar)
    'sample_received'
    >>> transitioned = do_action_for(fe, "submit")
    >>> transitioned[0]
    True
    >>> api.get_workflow_status_of(fe)
    'to_be_verified'

And I cannot resubmit again:

    >>> isTransitionAllowed(cu, "submit")
    False
    >>> isTransitionAllowed(fe, "submit")
    False

Deactivate the workflow sampling and rest `Cu` as a lab analysis:

    >>> Cu.setPointOfCapture("lab")
    >>> bikasetup.setSamplingWorkflowEnabled(False)


Auto submission of Analysis Requests when all its analyses are submitted
------------------------------------------------------------------------

Create an Analysis Request:

    >>> ar = new_ar([Cu, Fe, Au])

Set results for some of the analyses only:

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> analyses[0].setResult('12')
    >>> analyses[1].setResult('12')

We've set some results, but all analyses are still in `unassigned`:

    >>> map(api.get_workflow_status_of, analyses)
    ['unassigned', 'unassigned', 'unassigned']

Transition some of them:

    >>> transitioned = do_action_for(analyses[0], "submit")
    >>> transitioned[0]
    True

    >>> api.get_workflow_status_of(analyses[0])
    'to_be_verified'

    >>> transitioned = do_action_for(analyses[1], "submit")
    >>> transitioned[0]
    True

    >>> api.get_workflow_status_of(analyses[1])
    'to_be_verified'

The Analysis Request status is still in `sample_received`:

    >>> api.get_workflow_status_of(ar)
    'sample_received'

If we try to transition the remaining analysis w/o result, nothing happens:

    >>> transitioned = do_action_for(analyses[2], "submit")
    >>> transitioned[0]
    False

    >>> api.get_workflow_status_of(analyses[2])
    'unassigned'

    >>> api.get_workflow_status_of(ar)
    'sample_received'

Even if we try with an empty or None result:

    >>> analyses[2].setResult('')
    >>> transitioned = do_action_for(analyses[2], "submit")
    >>> transitioned[0]
    False

    >>> api.get_workflow_status_of(analyses[2])
    'unassigned'

    >>> analyses[2].setResult(None)
    >>> transitioned = do_action_for(analyses[2], "submit")
    >>> transitioned[0]
    False

    >>> api.get_workflow_status_of(analyses[2])
    'unassigned'

But will work if we try with a result of 0:

    >>> analyses[2].setResult(0)
    >>> transitioned = do_action_for(analyses[2], "submit")
    >>> transitioned[0]
    True

    >>> api.get_workflow_status_of(analyses[2])
    'to_be_verified'

And the AR will follow:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

And we cannot re-submit analyses that have been already submitted:

    >>> transitioned = do_action_for(analyses[2], "submit")
    >>> transitioned[0]
    False


Auto submission of a Worksheets when all its analyses are submitted
-------------------------------------------------------------------

The same behavior as for Analysis Requests applies to the worksheet when all its
analyses are submitted.

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

Set results and submit all analyses from the worksheet except one:

    >>> ws_analyses = worksheet.getAnalyses()
    >>> analysis_1 = analyses[0]
    >>> analysis_2 = analyses[1]
    >>> analysis_3 = analyses[2]
    >>> analysis_4 = analyses[3]

    >>> analysis_2.setResult('5')
    >>> transitioned = do_action_for(analysis_2, "submit")
    >>> transitioned[0]
    True

    >>> api.get_workflow_status_of(analysis_2)
    'to_be_verified'

    >>> analysis_3.setResult('6')
    >>> transitioned = do_action_for(analysis_3, "submit")
    >>> transitioned[0]
    True

    >>> api.get_workflow_status_of(analysis_3)
    'to_be_verified'

    >>> analysis_4.setResult('7')
    >>> transitioned = do_action_for(analysis_4, "submit")
    >>> transitioned[0]
    True

    >>> api.get_workflow_status_of(analysis_4)
    'to_be_verified'

The Analysis Request number 1 has been automatically transitioned because all
the contained analyses have been submitted:

    >>> api.get_workflow_status_of(ar1)
    'to_be_verified'

While Analysis Request number 0 has not been transitioned because still have two
analyses with results pending:

    >>> api.get_workflow_status_of(ar0)
    'sample_received'

And same with worksheet, cause there is one result pending:

    >>> api.get_workflow_status_of(worksheet)
    'open'

If we set a result for the pending analysis:

    >>> analysis_1.setResult('9')
    >>> transitioned = do_action_for(analysis_1, "submit")
    >>> transitioned[0]
    True

    >>> api.get_workflow_status_of(analysis_1)
    'to_be_verified'

The worksheet will follow:

    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'

But the Analysis Request number 0 will remain `sample_received`:

    >>> api.get_workflow_status_of(ar0)
    'sample_received'

Unless we submit a result for `Au` analysis:

    >>> au_an = filter(lambda an: an.getKeyword() == 'Au', analyses_ar0)[0]
    >>> au_an.setResult('10')
    >>> transitioned = do_action_for(au_an, "submit")
    >>> transitioned[0]
    True

    >>> api.get_workflow_status_of(au_an)
    'to_be_verified'

    >>> api.get_workflow_status_of(ar0)
    'to_be_verified'


Submission of results for analyses with interim fields set
----------------------------------------------------------

For an analysis to be submitted successfully, it must have a result set, but if
the analysis have interim fields, they are mandatory too:

    >>> Au.setInterimFields([
    ...     {"keyword": "interim_1", "title": "Interim 1",},
    ...     {"keyword": "interim_2", "title": "Interim 2",}])

Create an Analysis Request:

    >>> ar = new_ar([Au])
    >>> analysis = ar.getAnalyses(full_objects=True)[0]

Cannot submit if no result is set:

    >>> transitioned = do_action_for(analysis, "submit")
    >>> transitioned[0]
    False

    >>> api.get_workflow_status_of(analysis)
    'unassigned'

But even if we set a result, we cannot submit because interims are missing:

    >>> analysis.setResult(12)
    >>> analysis.getResult()
    '12'

    >>> transitioned = do_action_for(analysis, "submit")
    >>> transitioned[0]
    False

    >>> api.get_workflow_status_of(analysis)
    'unassigned'

So, if the analysis has interims defined, all them are required too:

    >>> analysis.setInterimValue("interim_1", 15)
    >>> analysis.getInterimValue("interim_1")
    '15'

    >>> analysis.getInterimValue("interim_2")
    ''

    >>> transitioned = do_action_for(analysis, "submit")
    >>> transitioned[0]
    False

    >>> api.get_workflow_status_of(analysis)
    'unassigned'

Even if we set a non-valid (None, empty value) to an interim:

    >>> analysis.setInterimValue("interim_2", None)
    >>> analysis.getInterimValue("interim_2")
    ''

    >>> transitioned = do_action_for(analysis, "submit")
    >>> transitioned[0]
    False

    >>> api.get_workflow_status_of(analysis)
    'unassigned'

    >>> analysis.setInterimValue("interim_2", '')
    >>> analysis.getInterimValue("interim_2")
    ''

    >>> transitioned = do_action_for(analysis, "submit")
    >>> transitioned[0]
    False

    >>> api.get_workflow_status_of(analysis)
    'unassigned'

But it will work if the value is 0:

    >>> analysis.setInterimValue("interim_2", 0)
    >>> analysis.getInterimValue("interim_2")
    '0'

    >>> transitioned = do_action_for(analysis, "submit")
    >>> transitioned[0]
    True

    >>> api.get_workflow_status_of(analysis)
    'to_be_verified'

And the Analysis Request follow:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

Might happen the other way round. We set interims but not a result:

    >>> ar = new_ar([Au])
    >>> analysis = ar.getAnalyses(full_objects=True)[0]
    >>> analysis.setInterimValue("interim_1", 10)
    >>> analysis.setInterimValue("interim_2", 20)

    >>> transitioned = do_action_for(analysis, "submit")
    >>> transitioned[0]
    False

    >>> api.get_workflow_status_of(analysis)
    'unassigned'

Still, the result is required:

    >>> analysis.setResult(12)
    >>> transitioned = do_action_for(analysis, "submit")
    >>> transitioned[0]
    True

    >>> api.get_workflow_status_of(analysis)
    'to_be_verified'

And again, the Analysis Request will follow:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'


Submission of results for analyses with interim calculation
-----------------------------------------------------------

If an analysis have a calculation assigned, the result will be calculated
automatically based on the calculation. If the calculation have interims set,
only those that do not have a default value set will be required.

Prepare the calculation and set the calculation to analysis `Au`:

    >>> Au.setInterimFields([])
    >>> calc = api.create(bikasetup.bika_calculations, 'Calculation', title='Test Calculation')
    >>> interim_1 = {'keyword': 'IT1', 'title': 'Interim 1', 'value': 10}
    >>> interim_2 = {'keyword': 'IT2', 'title': 'Interim 2', 'value': 2}
    >>> interim_3 = {'keyword': 'IT3', 'title': 'Interim 3', 'value': ''}
    >>> interim_4 = {'keyword': 'IT4', 'title': 'Interim 4', 'value': None}
    >>> interim_5 = {'keyword': 'IT5', 'title': 'Interim 5'}
    >>> interims = [interim_1, interim_2, interim_3, interim_4, interim_5]
    >>> calc.setInterimFields(interims)
    >>> calc.setFormula("[IT1]+[IT2]+[IT3]+[IT4]+[IT5]")
    >>> Au.setCalculation(calc)

Create an Analysis Request:

    >>> ar = new_ar([Au])
    >>> analysis = ar.getAnalyses(full_objects=True)[0]

Cannot submit if no result is set:

    >>> transitioned = do_action_for(analysis, "submit")
    >>> transitioned[0]
    False

    >>> api.get_workflow_status_of(analysis)
    'unassigned'

TODO This should not be like this, but the calculation is performed by
`ajaxCalculateAnalysisEntry`. The calculation logic must be moved to
'api.analysis.calculate`:

    >>> analysis.setResult("12")

Set a value for interim IT5:

    >>> analysis.setInterimValue("IT5", 5)

Cannot transition because IT3 and IT4 have None/empty values as default:

    >>> transitioned = do_action_for(analysis, "submit")
    >>> transitioned[0]
    False

    >>> api.get_workflow_status_of(analysis)
    'unassigned'

Let's set a value for those interims:

    >>> analysis.setInterimValue("IT3", 3)

    >>> transitioned = do_action_for(analysis, "submit")
    >>> transitioned[0]
    False

    >>> api.get_workflow_status_of(analysis)
    'unassigned'

    >>> analysis.setInterimValue("IT4", 4)

Since interims IT1 and IT2 have default values set, the analysis will submit:

    >>> transitioned = do_action_for(analysis, "submit")
    >>> transitioned[0]
    True

    >>> api.get_workflow_status_of(analysis)
    'to_be_verified'


Submission of results for analyses with dependencies
----------------------------------------------------

If an analysis is associated to a calculation that uses the result of other
analyses (dependents), then the analysis cannot be submitted unless all its
dependents were previously submitted.

Reset the interim fields for analysis `Au`:

    >>> Au.setInterimFields([])

Prepare a calculation that depends on `Cu` and assign it to `Fe` analysis:

    >>> calc_fe = api.create(bikasetup.bika_calculations, 'Calculation', title='Calc for Fe')
    >>> calc_fe.setFormula("[Cu]*10")
    >>> Fe.setCalculation(calc_fe)

Prepare a calculation that depends on `Fe` and assign it to `Au` analysis:

    >>> calc_au = api.create(bikasetup.bika_calculations, 'Calculation', title='Calc for Au')
    >>> interim_1 = {'keyword': 'IT1', 'title': 'Interim 1'}
    >>> calc_au.setInterimFields([interim_1])
    >>> calc_au.setFormula("([IT1]+[Fe])/2")
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

    >>> fe_analysis.setResult(12)
    >>> au_analysis.setResult(10)

Cannot submit `Fe`, because there is no result for `Cu` yet:

    >>> transitioned = do_action_for(fe_analysis, "submit")
    >>> transitioned[0]
    False

    >>> api.get_workflow_status_of(fe_analysis)
    'unassigned'

And we cannot submit `Au`, because `Cu`, a dependency of `Fe`, has no result:

    >>> transitioned = do_action_for(au_analysis, "submit")
    >>> transitioned[0]
    False

    >>> api.get_workflow_status_of(au_analysis)
    'unassigned'

Set a result for `Cu` and submit:

    >>> cu_analysis.setResult(12)
    >>> transitioned = do_action_for(cu_analysis, "submit")
    >>> transitioned[0]
    True

    >>> api.get_workflow_status_of(cu_analysis)
    'to_be_verified'

But `Fe` won't follow, cause only dependencies follow, but not dependents:

    >>> api.get_workflow_status_of(fe_analysis)
    'unassigned'

If we try to submit `Au`, the submission will not take place:

    >>> transitioned = do_action_for(au_analysis, "submit")
    >>> transitioned[0]
    False

    >>> api.get_workflow_status_of(au_analysis)
    'unassigned'

Because of the missing interim. Set the interim for `Au`:

    >>> au_analysis.setInterimValue("IT1", 4)

And now we are able to submit `Au`:

    >>> transitioned = do_action_for(au_analysis, "submit")
    >>> transitioned[0]
    True

    >>> api.get_workflow_status_of(au_analysis)
    'to_be_verified'

And since `Fe` is a dependency of `Au`, `Fe` will be automatically transitioned:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

As well as the Analysis Request:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'


Check permissions for Submit transition
---------------------------------------

Create an Analysis Request:

    >>> ar = new_ar([Cu])

The status of the Analysis Request is `sample_received`:

    >>> api.get_workflow_status_of(ar)
    'sample_received'

And the status of the Analysis is `unassigned`:

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> map(api.get_workflow_status_of, analyses)
    ['unassigned']

Set a result:

    >>> analysis = analyses[0]
    >>> analysis.setResult(23)

Exactly these roles can submit:

    >>> get_roles_for_permission("senaite.core: Edit Results", analysis)
    ['Analyst', 'LabManager', 'Manager']

    >>> get_roles_for_permission("senaite.core: Edit Field Results", analysis)
    ['LabManager', 'Manager', 'Sampler']

And these roles can view results:

    >>> get_roles_for_permission("senaite.core: View Results", analysis)
    ['Analyst', 'LabClerk', 'LabManager', 'Manager', 'RegulatoryInspector']

Current user can submit because has the `LabManager` role:

    >>> isTransitionAllowed(analysis, "submit")
    True

But cannot for other roles:

    >>> setRoles(portal, TEST_USER_ID, ['Authenticated', 'LabClerk', 'RegulatoryInspector'])
    >>> isTransitionAllowed(analysis, "submit")
    False

Even if is `Owner`

    >>> setRoles(portal, TEST_USER_ID, ['Owner'])
    >>> isTransitionAllowed(analysis, "submit")
    False

And Clients cannot neither:

    >>> setRoles(portal, TEST_USER_ID, ['Client'])
    >>> isTransitionAllowed(analysis, "submit")
    False

Reset the roles for current user:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
