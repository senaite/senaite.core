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
