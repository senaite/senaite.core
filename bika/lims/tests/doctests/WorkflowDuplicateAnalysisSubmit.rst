Duplicate Analysis submission guard and event
=============================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowDuplicateAnalysisSubmit


Test Setup
----------

Needed Imports:

    >>> import transaction
    >>> from DateTime import DateTime
    >>> from plone import api as ploneapi

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for


Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

Needed Imports:

    >>> import re
    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.content.analysisrequest import AnalysisRequest
    >>> from bika.lims.content.sample import Sample
    >>> from bika.lims.content.samplepartition import SamplePartition
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.sample import create_sample
    >>> from bika.lims.utils import tmpID
    >>> from bika.lims.workflow import doActionFor
    >>> from bika.lims.workflow import getCurrentState
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from DateTime import DateTime
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from plone.app.testing import setRoles

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)
    ...
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
    ...
    >>> def to_new_worksheet_with_duplicate(ar):
    ...     worksheet = api.create(portal.worksheets, "Worksheet")
    ...     for analysis in ar.getAnalyses(full_objects=True):
    ...         worksheet.addAnalysis(analysis)
    ...     worksheet.addDuplicateAnalyses(1)
    ...     return worksheet
    ...
    >>> def submit_regular_analyses(worksheet):
    ...     for analysis in worksheet.getRegularAnalyses():
    ...         analysis.setResult(13)
    ...         do_action_for(analysis, "submit")
    ...
    >>> def try_transition(object, transition_id, target_state_id):
    ...      success = do_action_for(object, transition_id)[0]
    ...      state = api.get_workflow_status_of(duplicate)
    ...      return success and state == target_state_id
    ...

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


Duplicate submission basic constraints
--------------------------------------

Create a Worksheet and submit regular analyses:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> worksheet = to_new_worksheet_with_duplicate(ar)
    >>> submit_regular_analyses(worksheet)

Get a duplicate:

    >>> duplicate = worksheet.getDuplicateAnalyses()[0]

Cannot submit a duplicate without a result:

    >>> try_transition(duplicate, "submit", "to_be_verified")
    False

Even if we try with an empty or None result:

    >>> duplicate.setResult('')
    >>> try_transition(duplicate, "submit", "to_be_verified")
    False

    >>> duplicate.setResult(None)
    >>> try_transition(duplicate, "submit", "to_be_verified")
    False

But will work if we try with a result of 0:

    >>> duplicate.setResult(0)
    >>> try_transition(duplicate, "submit", "to_be_verified")
    True

    >>> api.get_workflow_status_of(duplicate)
    'to_be_verified'

And we cannot re-submit a duplicate that have been submitted already:

    >>> try_transition(duplicate, "submit", "to_be_verified")
    False


Auto submission of a Worksheets when all its analyses are submitted
-------------------------------------------------------------------

Create an Analysis Request:

    >>> ar = new_ar([Cu, Fe, Au])

Create a worksheet:

    >>> worksheet = api.create(portal.worksheets, "Worksheet")

And assign all analyses from the Analysis Request created before:

    >>> for analysis in ar.getAnalyses(full_objects=True):
    ...     worksheet.addAnalysis(analysis)

Add a Duplicate of sample from position 1:

    >>> duplicates = worksheet.addDuplicateAnalyses(1)

Set results and submit all analyses from the worksheet except the duplicates:

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

Because duplicates are still in `assigned` state:

    >>> map(api.get_workflow_status_of, worksheet.getDuplicateAnalyses())
    ['assigned', 'assigned', 'assigned']

If we set results and submit duplicates:

    >>> for analysis in worksheet.getDuplicateAnalyses():
    ...     analysis.setResult(13)
    ...     transitioned = do_action_for(analysis, "submit")
    >>> map(api.get_workflow_status_of, worksheet.getDuplicateAnalyses())
    ['to_be_verified', 'to_be_verified', 'to_be_verified']

The worksheet will automatically be submitted too:

    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'


Submission of duplicates with interim fields set
------------------------------------------------

Set interims to the analysis `Au`:

    >>> Au.setInterimFields([
    ...     {"keyword": "interim_1", "title": "Interim 1",},
    ...     {"keyword": "interim_2", "title": "Interim 2",}])

Create a Worksheet and submit regular analyses:

    >>> ar = new_ar([Au])
    >>> worksheet = to_new_worksheet_with_duplicate(ar)
    >>> submit_regular_analyses(worksheet)

Get the duplicate:

    >>> duplicate = worksheet.getDuplicateAnalyses()[0]

Cannot submit if no result is set:

    >>> try_transition(duplicate, "submit", "to_be_verified")
    False

But even if we set a result, we cannot submit because interims are missing:

    >>> duplicate.setResult(12)
    >>> duplicate.getResult()
    '12'

    >>> try_transition(duplicate, "submit", "to_be_verified")
    False

So, if the duplicate has interims defined, all them are required too:

    >>> duplicate.setInterimValue("interim_1", 15)
    >>> duplicate.getInterimValue("interim_1")
    '15'

    >>> duplicate.getInterimValue("interim_2")
    ''

    >>> try_transition(duplicate, "submit", "to_be_verified")
    False

Even if we set a non-valid (None, empty) value to an interim:

    >>> duplicate.setInterimValue("interim_2", None)
    >>> duplicate.getInterimValue("interim_2")
    ''

    >>> try_transition(duplicate, "submit", "to_be_verified")
    False

    >>> duplicate.setInterimValue("interim_2", '')
    >>> duplicate.getInterimValue("interim_2")
    ''

    >>> try_transition(duplicate, "submit", "to_be_verified")
    False

But it will work if the value is 0:

    >>> duplicate.setInterimValue("interim_2", 0)
    >>> duplicate.getInterimValue("interim_2")
    '0'

    >>> try_transition(duplicate, "submit", "to_be_verified")
    True

    >>> api.get_workflow_status_of(duplicate)
    'to_be_verified'

Might happen the other way round. We set interims but not a result:

    >>> ar = new_ar([Au])
    >>> worksheet = to_new_worksheet_with_duplicate(ar)
    >>> submit_regular_analyses(worksheet)
    >>> duplicate = worksheet.getDuplicateAnalyses()[0]
    >>> duplicate.setInterimValue("interim_1", 10)
    >>> duplicate.setInterimValue("interim_2", 20)
    >>> try_transition(duplicate, "submit", "to_be_verified")
    False

Still, the result is required:

    >>> duplicate.setResult(12)
    >>> try_transition(duplicate, "submit", "to_be_verified")
    True

    >>> api.get_workflow_status_of(duplicate)
    'to_be_verified'


Submission of duplicates with interim calculation
-------------------------------------------------

If a duplicate have a calculation assigned, the result will be calculated
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

Create a Worksheet and submit regular analyses:

    >>> ar = new_ar([Au])
    >>> worksheet = to_new_worksheet_with_duplicate(ar)

Cannot submit if no result is set

    >>> duplicate = worksheet.getDuplicateAnalyses()[0]
    >>> try_transition(duplicate, "submit", "to_be_verified")
    False

TODO This should not be like this, but the calculation is performed by
`ajaxCalculateAnalysisEntry`. The calculation logic must be moved to
'api.analysis.calculate`:

    >>> duplicate.setResult(34)

Set a value for interim IT5:

    >>> duplicate.setInterimValue("IT5", 5)

Cannot transition because IT3 and IT4 have None/empty values as default:

    >>> try_transition(duplicate, "submit", "to_be_verified")
    False

Let's set a value for those interims:

    >>> duplicate.setInterimValue("IT3", 3)
    >>> try_transition(duplicate, "submit", "to_be_verified")
    False

    >>> duplicate.setInterimValue("IT4", 4)

Since interims IT1 and IT2 have default values set, the analysis will submit:

    >>> try_transition(duplicate, "submit", "to_be_verified")
    True

    >>> api.get_workflow_status_of(duplicate)
    'to_be_verified'
