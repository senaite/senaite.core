Reference Analysis (Controls) submission guard and event
========================================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowReferenceAnalysisControlSubmit


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

Functional Helpers:

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
    ...                      control=False, ExpiryDate=date_future,
    ...                      ReferenceResults=control_refs)

control submission basic constraints
------------------------------------

Create a Worksheet and submit regular analyses:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> worksheet = to_new_worksheet_with_reference(ar, control_sample)
    >>> submit_regular_analyses(worksheet)

Get control analyses:

    >>> controls = worksheet.getReferenceAnalyses()
    >>> control_1 = controls[0]
    >>> control_2 = controls[1]
    >>> control_3 = controls[2]

Cannot submit a control without a result:

    >>> try_transition(control_1, "submit", "to_be_verified")
    False

Even if we try with an empty or None result:

    >>> control_1.setResult('')
    >>> try_transition(control_1, "submit", "to_be_verified")
    False

    >>> control_1.setResult(None)
    >>> try_transition(control_1, "submit", "to_be_verified")
    False

But will work if we try with a result of 0:

    >>> control_1.setResult(0)
    >>> try_transition(control_1, "submit", "to_be_verified")
    True

    >>> api.get_workflow_status_of(control_1)
    'to_be_verified'

And we cannot re-submit a control that have been submitted already:

    >>> try_transition(control_1, "submit", "to_be_verified")
    False


Auto submission of a Worksheets when all its analyses are submitted
-------------------------------------------------------------------

Create a Worksheet:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> worksheet = to_new_worksheet_with_reference(ar, control_sample)

Set results and submit all analyses from the worksheet except controls:

    >>> for analysis in worksheet.getRegularAnalyses():
    ...     analysis.setResult(13)
    ...     transitioned = do_action_for(analysis, "submit")
    >>> map(api.get_workflow_status_of, worksheet.getRegularAnalyses())
    ['to_be_verified', 'to_be_verified', 'to_be_verified']

While the Analysis Request has been transitioned to `to_be_verified`:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

The worksheet has not been transitioned:

    >>> api.get_workflow_status_of(worksheet)
    'open'

Because controls are still in `assigned` state:

    >>> map(api.get_workflow_status_of, worksheet.getReferenceAnalyses())
    ['assigned', 'assigned', 'assigned']

If we set results and submit controls:

    >>> for analysis in worksheet.getReferenceAnalyses():
    ...     analysis.setResult(0)
    ...     transitioned = do_action_for(analysis, "submit")
    >>> map(api.get_workflow_status_of, worksheet.getReferenceAnalyses())
    ['to_be_verified', 'to_be_verified', 'to_be_verified']

The worksheet will automatically be submitted too:

    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'


Submission of controls with interim fields set
----------------------------------------------

Set interims to the analysis `Au`:

    >>> Au.setInterimFields([
    ...     {"keyword": "interim_1", "title": "Interim 1",},
    ...     {"keyword": "interim_2", "title": "Interim 2",}])

Create a Worksheet and submit regular analyses:

    >>> ar = new_ar([Au])
    >>> worksheet = to_new_worksheet_with_reference(ar, control_sample)
    >>> submit_regular_analyses(worksheet)

Get control analyses:

    >>> control = worksheet.getReferenceAnalyses()[0]

Cannot submit if no result is set:

    >>> try_transition(control, "submit", "to_be_verified")
    False

But even if we set a result, we cannot submit because interims are missing:

    >>> control.setResult(12)
    >>> control.getResult()
    '12'

    >>> try_transition(control, "submit", "to_be_verified")
    False

So, if the control has interims defined, all them are required too:

    >>> control.setInterimValue("interim_1", 15)
    >>> control.getInterimValue("interim_1")
    '15'

    >>> control.getInterimValue("interim_2")
    ''

    >>> try_transition(control, "submit", "to_be_verified")
    False

Even if we set a non-valid (None, empty) value to an interim:

    >>> control.setInterimValue("interim_2", None)
    >>> control.getInterimValue("interim_2")
    ''

    >>> try_transition(control, "submit", "to_be_verified")
    False

    >>> control.setInterimValue("interim_2", '')
    >>> control.getInterimValue("interim_2")
    ''

    >>> try_transition(control, "submit", "to_be_verified")
    False

But it will work if the value is 0:

    >>> control.setInterimValue("interim_2", 0)
    >>> control.getInterimValue("interim_2")
    '0'

    >>> try_transition(control, "submit", "to_be_verified")
    True

    >>> api.get_workflow_status_of(control)
    'to_be_verified'

Might happen the other way round. We set interims but not a result:

    >>> ar = new_ar([Au])
    >>> worksheet = to_new_worksheet_with_reference(ar, control_sample)
    >>> submit_regular_analyses(worksheet)
    >>> control = worksheet.getReferenceAnalyses()[0]
    >>> control.setInterimValue("interim_1", 10)
    >>> control.setInterimValue("interim_2", 20)
    >>> try_transition(control, "submit", "to_be_verified")
    False

Still, the result is required:

    >>> control.setResult(12)
    >>> try_transition(control, "submit", "to_be_verified")
    True

    >>> api.get_workflow_status_of(control)
    'to_be_verified'


Submission of control analysis with interim calculation
-------------------------------------------------------

If a control analysis have a calculation assigned, the result will be calculated
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

Create a Worksheet with control:

    >>> ar = new_ar([Au])
    >>> worksheet = to_new_worksheet_with_reference(ar, control_sample)

Cannot submit if no result is set

    >>> control = worksheet.getReferenceAnalyses()[0]
    >>> try_transition(control, "submit", "to_be_verified")
    False

TODO This should not be like this, but the calculation is performed by
`ajaxCalculateAnalysisEntry`. The calculation logic must be moved to
'api.analysis.calculate`:

    >>> control.setResult(34)

Set a value for interim IT5:

    >>> control.setInterimValue("IT5", 5)

Cannot transition because IT3 and IT4 have None/empty values as default:

    >>> try_transition(control, "submit", "to_be_verified")
    False

Let's set a value for those interims:

    >>> control.setInterimValue("IT3", 3)
    >>> try_transition(control, "submit", "to_be_verified")
    False

    >>> control.setInterimValue("IT4", 4)

Since interims IT1 and IT2 have default values set, the analysis will submit:

    >>> try_transition(control, "submit", "to_be_verified")
    True

    >>> api.get_workflow_status_of(control)
    'to_be_verified'


Submission of controls with dependencies
----------------------------------------

controls with dependencies are not allowed. controls can only be created
from analyses without dependents.

TODO Might we consider to allow the creation of controls with dependencies?

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

Create a Worksheet with control:

    >>> worksheet = to_new_worksheet_with_reference(ar, control_sample)
    >>> analyses = worksheet.getRegularAnalyses()

Only one control created for `Cu`, cause is the only analysis that does not
have dependents:

    >>> controls = worksheet.getReferenceAnalyses()
    >>> len(controls) == 1
    True

    >>> control = controls[0]
    >>> control.getKeyword()
    'Cu'

TODO This should not be like this, but the calculation is performed by
`ajaxCalculateAnalysisEntry`. The calculation logic must be moved to
'api.analysis.calculate`:

    >>> control.setResult(0)

Cannot submit routine `Fe` cause there is no result for routine analysis `Cu`
and the control of `Cu` cannot be used as a dependent:

    >>> fe_analysis = filter(lambda an: an.getKeyword()=="Fe", analyses)[0]
    >>> try_transition(fe_analysis, "submit", "to_be_verified")
    False


Check permissions for Submit transition
---------------------------------------

Create a Worksheet and submit regular analyses:

    >>> ar = new_ar([Cu])
    >>> worksheet = to_new_worksheet_with_reference(ar, control_sample)
    >>> submit_regular_analyses(worksheet)

Set a result:

    >>> control = worksheet.getReferenceAnalyses()[0]
    >>> control.setResult(23)

Exactly these roles can submit:

    >>> get_roles_for_permission("senaite.core: Edit Results", control)
    ['Analyst', 'LabManager', 'Manager']

And these roles can view results:

    >>> get_roles_for_permission("senaite.core: View Results", control)
    ['Analyst', 'LabClerk', 'LabManager', 'Manager', 'RegulatoryInspector']

Current user can submit because has the `LabManager` role:

    >>> isTransitionAllowed(control, "submit")
    True

But cannot for other roles:

    >>> setRoles(portal, TEST_USER_ID, ['Authenticated', 'LabClerk', 'RegulatoryInspector', 'Sampler'])
    >>> isTransitionAllowed(control, "submit")
    False

Even if is `Owner`

    >>> setRoles(portal, TEST_USER_ID, ['Owner'])
    >>> isTransitionAllowed(control, "submit")
    False

And Clients cannot neither:

    >>> setRoles(portal, TEST_USER_ID, ['Client'])
    >>> isTransitionAllowed(control, "submit")
    False

Reset the roles for current user:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
