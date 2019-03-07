Reference Analysis (Blanks) submission guard and event
======================================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowReferenceAnalysisBlankSubmit


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
    >>> blank_def = api.create(bikasetup.bika_referencedefinitions, "ReferenceDefinition", title="Blank definition", Blank=True)
    >>> blank_refs = [{'uid': api.get_uid(Cu), 'result': '0', 'min': '0', 'max': '0'},
    ...               {'uid': api.get_uid(Fe), 'result': '0', 'min': '0', 'max': '0'},
    ...               {'uid': api.get_uid(Au), 'result': '0', 'min': '0', 'max': '0'},]
    >>> blank_def.setReferenceResults(blank_refs)
    >>> control_def = api.create(bikasetup.bika_referencedefinitions, "ReferenceDefinition", title="Control definition")
    >>> control_refs = [{'uid': api.get_uid(Cu), 'result': '10', 'min': '0', 'max': '0'},
    ...                 {'uid': api.get_uid(Fe), 'result': '10', 'min': '0', 'max': '0'},
    ...                 {'uid': api.get_uid(Au), 'result': '15', 'min': '14.5', 'max': '15.5'},]
    >>> control_def.setReferenceResults(control_refs)
    >>> blank_sample = api.create(supplier, "ReferenceSample", title="Blank",
    ...                    ReferenceDefinition=blank_def,
    ...                    Blank=True, ExpiryDate=date_future,
    ...                    ReferenceResults=blank_refs)
    >>> control_sample = api.create(supplier, "ReferenceSample", title="Control",
    ...                      ReferenceDefinition=control_def,
    ...                      Blank=False, ExpiryDate=date_future,
    ...                      ReferenceResults=control_refs)

Blank submission basic constraints
----------------------------------

Create a Worksheet and submit regular analyses:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> worksheet = to_new_worksheet_with_reference(ar, blank_sample)
    >>> submit_regular_analyses(worksheet)

Get blank analyses:

    >>> blanks = worksheet.getReferenceAnalyses()
    >>> blank_1 = blanks[0]
    >>> blank_2 = blanks[1]
    >>> blank_3 = blanks[2]

Cannot submit a blank without a result:

    >>> try_transition(blank_1, "submit", "to_be_verified")
    False

Even if we try with an empty or None result:

    >>> blank_1.setResult('')
    >>> try_transition(blank_1, "submit", "to_be_verified")
    False

    >>> blank_1.setResult(None)
    >>> try_transition(blank_1, "submit", "to_be_verified")
    False

But will work if we try with a result of 0:

    >>> blank_1.setResult(0)
    >>> try_transition(blank_1, "submit", "to_be_verified")
    True

    >>> api.get_workflow_status_of(blank_1)
    'to_be_verified'

And we cannot re-submit a blank that have been submitted already:

    >>> try_transition(blank_1, "submit", "to_be_verified")
    False


Auto submission of a Worksheets when all its analyses are submitted
-------------------------------------------------------------------

Create a Worksheet:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> worksheet = to_new_worksheet_with_reference(ar, blank_sample)

Set results and submit all analyses from the worksheet except blanks:

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

Because blanks are still in `assigned` state:

    >>> map(api.get_workflow_status_of, worksheet.getReferenceAnalyses())
    ['assigned', 'assigned', 'assigned']

If we set results and submit blanks:

    >>> for analysis in worksheet.getReferenceAnalyses():
    ...     analysis.setResult(0)
    ...     transitioned = do_action_for(analysis, "submit")
    >>> map(api.get_workflow_status_of, worksheet.getReferenceAnalyses())
    ['to_be_verified', 'to_be_verified', 'to_be_verified']

The worksheet will automatically be submitted too:

    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'


Submission of blanks with interim fields set
--------------------------------------------

Set interims to the analysis `Au`:

    >>> Au.setInterimFields([
    ...     {"keyword": "interim_1", "title": "Interim 1",},
    ...     {"keyword": "interim_2", "title": "Interim 2",}])

Create a Worksheet and submit regular analyses:

    >>> ar = new_ar([Au])
    >>> worksheet = to_new_worksheet_with_reference(ar, blank_sample)
    >>> submit_regular_analyses(worksheet)

Get blank analyses:

    >>> blank = worksheet.getReferenceAnalyses()[0]

Cannot submit if no result is set:

    >>> try_transition(blank, "submit", "to_be_verified")
    False

But even if we set a result, we cannot submit because interims are missing:

    >>> blank.setResult(12)
    >>> blank.getResult()
    '12'

    >>> try_transition(blank, "submit", "to_be_verified")
    False

So, if the blank has interims defined, all them are required too:

    >>> blank.setInterimValue("interim_1", 15)
    >>> blank.getInterimValue("interim_1")
    '15'

    >>> blank.getInterimValue("interim_2")
    ''

    >>> try_transition(blank, "submit", "to_be_verified")
    False

Even if we set a non-valid (None, empty) value to an interim:

    >>> blank.setInterimValue("interim_2", None)
    >>> blank.getInterimValue("interim_2")
    ''

    >>> try_transition(blank, "submit", "to_be_verified")
    False

    >>> blank.setInterimValue("interim_2", '')
    >>> blank.getInterimValue("interim_2")
    ''

    >>> try_transition(blank, "submit", "to_be_verified")
    False

But it will work if the value is 0:

    >>> blank.setInterimValue("interim_2", 0)
    >>> blank.getInterimValue("interim_2")
    '0'

    >>> try_transition(blank, "submit", "to_be_verified")
    True

    >>> api.get_workflow_status_of(blank)
    'to_be_verified'

Might happen the other way round. We set interims but not a result:

    >>> ar = new_ar([Au])
    >>> worksheet = to_new_worksheet_with_reference(ar, blank_sample)
    >>> submit_regular_analyses(worksheet)
    >>> blank = worksheet.getReferenceAnalyses()[0]
    >>> blank.setInterimValue("interim_1", 10)
    >>> blank.setInterimValue("interim_2", 20)
    >>> try_transition(blank, "submit", "to_be_verified")
    False

Still, the result is required:

    >>> blank.setResult(12)
    >>> try_transition(blank, "submit", "to_be_verified")
    True

    >>> api.get_workflow_status_of(blank)
    'to_be_verified'


Submission of blank analysis with interim calculation
-----------------------------------------------------

If a blank analysis have a calculation assigned, the result will be calculated
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

Create a Worksheet with blank:

    >>> ar = new_ar([Au])
    >>> worksheet = to_new_worksheet_with_reference(ar, blank_sample)

Cannot submit if no result is set

    >>> blank = worksheet.getReferenceAnalyses()[0]
    >>> try_transition(blank, "submit", "to_be_verified")
    False

TODO This should not be like this, but the calculation is performed by
`ajaxCalculateAnalysisEntry`. The calculation logic must be moved to
'api.analysis.calculate`:

    >>> blank.setResult(34)

Set a value for interim IT5:

    >>> blank.setInterimValue("IT5", 5)

Cannot transition because IT3 and IT4 have None/empty values as default:

    >>> try_transition(blank, "submit", "to_be_verified")
    False

Let's set a value for those interims:

    >>> blank.setInterimValue("IT3", 3)
    >>> try_transition(blank, "submit", "to_be_verified")
    False

    >>> blank.setInterimValue("IT4", 4)

Since interims IT1 and IT2 have default values set, the analysis will submit:

    >>> try_transition(blank, "submit", "to_be_verified")
    True

    >>> api.get_workflow_status_of(blank)
    'to_be_verified'


Submission of blanks with dependencies
--------------------------------------

Blanks with dependencies are not allowed. Blanks can only be created
from analyses without dependents.

TODO Might we consider to allow the creation of blanks with dependencies?

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

Create a Worksheet with blank:

    >>> worksheet = to_new_worksheet_with_reference(ar, blank_sample)
    >>> analyses = worksheet.getRegularAnalyses()

Only one blank created for `Cu`, cause is the only analysis that does not
have dependents:

    >>> blanks = worksheet.getReferenceAnalyses()
    >>> len(blanks) == 1
    True

    >>> blank = blanks[0]
    >>> blank.getKeyword()
    'Cu'

TODO This should not be like this, but the calculation is performed by
`ajaxCalculateAnalysisEntry`. The calculation logic must be moved to
'api.analysis.calculate`:

    >>> blank.setResult(0)

Cannot submit routine `Fe` cause there is no result for routine analysis `Cu`
and the blank of `Cu` cannot be used as a dependent:

    >>> fe_analysis = filter(lambda an: an.getKeyword()=="Fe", analyses)[0]
    >>> try_transition(fe_analysis, "submit", "to_be_verified")
    False


Check permissions for Submit transition
---------------------------------------

Create a Worksheet and submit regular analyses:

    >>> ar = new_ar([Cu])
    >>> worksheet = to_new_worksheet_with_reference(ar, blank_sample)
    >>> submit_regular_analyses(worksheet)

Set a result:

    >>> blank = worksheet.getReferenceAnalyses()[0]
    >>> blank.setResult(23)

Exactly these roles can submit:

    >>> get_roles_for_permission("senaite.core: Edit Results", blank)
    ['Analyst', 'LabManager', 'Manager']

And these roles can view results:

    >>> get_roles_for_permission("senaite.core: View Results", blank)
    ['Analyst', 'LabClerk', 'LabManager', 'Manager', 'RegulatoryInspector']

Current user can submit because has the `LabManager` role:

    >>> isTransitionAllowed(blank, "submit")
    True

But cannot for other roles:

    >>> setRoles(portal, TEST_USER_ID, ['Authenticated', 'LabClerk', 'RegulatoryInspector', 'Sampler'])
    >>> isTransitionAllowed(blank, "submit")
    False

Even if is `Owner`

    >>> setRoles(portal, TEST_USER_ID, ['Owner'])
    >>> isTransitionAllowed(blank, "submit")
    False

And Clients cannot neither:

    >>> setRoles(portal, TEST_USER_ID, ['Client'])
    >>> isTransitionAllowed(blank, "submit")
    False

Reset the roles for current user:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
