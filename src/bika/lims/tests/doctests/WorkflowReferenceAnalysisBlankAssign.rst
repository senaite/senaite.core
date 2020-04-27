Reference Analysis (Blanks) assign guard and event
==================================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowReferenceAnalysisBlankAssign


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
    ...     return ar

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
    >>> ref_def = api.create(bikasetup.bika_referencedefinitions, "ReferenceDefinition", title="Blank definition", Blank=True)
    >>> ref_refs = [{'uid': api.get_uid(Cu), 'result': '0', 'min': '0', 'max': '0'},
    ...             {'uid': api.get_uid(Fe), 'result': '0', 'min': '0', 'max': '0'},
    ...             {'uid': api.get_uid(Au), 'result': '0', 'min': '0', 'max': '0'},]
    >>> ref_def.setReferenceResults(ref_refs)
    >>> ref_sample = api.create(supplier, "ReferenceSample", title="Blank",
    ...                    ReferenceDefinition=ref_def,
    ...                    Blank=True, ExpiryDate=date_future,
    ...                    ReferenceResults=ref_refs)

Assign transition and guard basic constraints
---------------------------------------------

Create an Analysis Request:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> transitioned = do_action_for(ar, "receive")
    >>> analyses = ar.getAnalyses(full_objects=True)

Create a Worksheet and add the analyses:

    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> for analysis in analyses:
    ...     worksheet.addAnalysis(analysis)

Add a blank:

    >>> ref_analyses = worksheet.addReferenceAnalyses(ref_sample, [Cu, Fe, Au])
    >>> len(ref_analyses)
    3

The status of the reference analyses is `assigned`:

    >>> ref_analyses = worksheet.getReferenceAnalyses()
    >>> map(api.get_workflow_status_of, ref_analyses)
    ['assigned', 'assigned', 'assigned']

All them are blanks:

    >>> map(lambda ref: ref.getReferenceType(), ref_analyses)
    ['b', 'b', 'b']

And are associated to the worksheet:

    >>> wuid = list(set(map(lambda ref: ref.getWorksheetUID(), ref_analyses)))
    >>> len(wuid)
    1
    >>> wuid[0] == api.get_uid(worksheet)
    True

Blanks do not have an Analyst assigned, though:

    >>> list(set(map(lambda ref: ref.getAnalyst(), ref_analyses)))
    ['']

If I assign a user to the Worksheet, same user will be assigned to analyses:

    >>> worksheet.setAnalyst(TEST_USER_ID)
    >>> worksheet.getAnalyst() == TEST_USER_ID
    True

    >>> filter(lambda an: an.getAnalyst() != TEST_USER_ID, analyses)
    []

And to the blanks as well:

    >>> filter(lambda an: an.getAnalyst() != TEST_USER_ID, ref_analyses)
    []

I can remove one of the blanks from the Worksheet:

    >>> ref = ref_analyses[0]
    >>> ref_uid = api.get_uid(ref)
    >>> worksheet.removeAnalysis(ref)
    >>> len(worksheet.getReferenceAnalyses())
    2

And the removed blank no longer exists:

    >>> api.get_object_by_uid(ref_uid, None) is None
    True

From `assigned` state I can do submit:

    >>> ref_analyses = worksheet.getReferenceAnalyses()
    >>> map(api.get_workflow_status_of, ref_analyses)
    ['assigned', 'assigned']
    >>> ref_analyses[0].setResult(20)
    >>> try_transition(ref_analyses[0], "submit", "to_be_verified")
    True

And blanks transition to `to_be_verified`:

    >>> map(api.get_workflow_status_of, ref_analyses)
    ['to_be_verified', 'assigned']

While keeping the Analyst that was assigned to the worksheet:

    >>> filter(lambda an: an.getAnalyst() != TEST_USER_ID, ref_analyses)
    []

And since there is still regular analyses in the Worksheet not yet submitted,
the Worksheet remains in `open` state:

    >>> api.get_workflow_status_of(worksheet)
    'open'

I submit the results for the rest of analyses:

    >>> for analysis in worksheet.getRegularAnalyses():
    ...     analysis.setResult(10)
    ...     transitioned = do_action_for(analysis, "submit")
    >>> map(api.get_workflow_status_of, worksheet.getRegularAnalyses())
    ['to_be_verified', 'to_be_verified', 'to_be_verified']

And since there is a blank that has not been yet submitted, the Worksheet
remains in `open` state:

    >>> ref = worksheet.getReferenceAnalyses()[1]
    >>> api.get_workflow_status_of(ref)
    'assigned'
    >>> api.get_workflow_status_of(worksheet)
    'open'

But if I remove the blank that has not been yet submitted, the status of the
Worksheet is promoted to `to_be_verified`, cause all the rest are in
`to_be_verified` state:

    >>> ref_uid = api.get_uid(ref)
    >>> worksheet.removeAnalysis(ref)
    >>> len(worksheet.getReferenceAnalyses())
    1
    >>> api.get_object_by_uid(ref_uid, None) is None
    True
    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'

And the blank itself no longer exists in the system:

    >>> api.get_object_by_uid(ref_uid, None) == None
    True

And now, I cannot add blanks anymore:

    >>> worksheet.addReferenceAnalyses(ref_sample, [Cu, Fe, Au])
    []
    >>> len(worksheet.getReferenceAnalyses())
    1


Check permissions for Assign transition
---------------------------------------

Create an Analysis Request:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> transitioned = do_action_for(ar, "receive")
    >>> analyses = ar.getAnalyses(full_objects=True)

Create a Worksheet and add the analyses:

    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> for analysis in analyses:
    ...     worksheet.addAnalysis(analysis)

Add blank analyses:

    >>> len(worksheet.addReferenceAnalyses(ref_sample, [Cu, Fe, Au]))
    3

Since a reference analysis can only live inside a Worksheet, the initial state
of the blank is `assigned` by default:

    >>> duplicates = worksheet.getReferenceAnalyses()
    >>> map(api.get_workflow_status_of, duplicates)
    ['assigned', 'assigned', 'assigned']
