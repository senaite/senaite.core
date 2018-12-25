Reference Analysis retract guard and event
==========================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowReferenceAnalysisRetract


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
    ...                      Blank=False, ExpiryDate=date_future,
    ...                      ReferenceResults=control_refs)


Retract transition and guard basic constraints
----------------------------------------------

Create an Analysis Request and submit regular analyses:

    >>> ar = new_ar([Cu])
    >>> worksheet = to_new_worksheet_with_reference(ar, control_sample)
    >>> submit_regular_analyses(worksheet)

Get the reference and submit:

    >>> reference = worksheet.getReferenceAnalyses()[0]
    >>> reference.setResult(12)
    >>> try_transition(reference, "submit", "to_be_verified")
    True
    >>> api.get_workflow_status_of(reference)
    'to_be_verified'
    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'

Retract the reference:

    >>> try_transition(reference, "retract", "retracted")
    True
    >>> api.get_workflow_status_of(reference)
    'retracted'

And one new additional reference has been added in `assigned` state:

    >>> references = worksheet.getReferenceAnalyses()
    >>> sorted(map(api.get_workflow_status_of, references))
    ['assigned', 'retracted']

And the Worksheet has been transitioned to `open`:

    >>> api.get_workflow_status_of(worksheet)
    'open'

While the Analysis Request is still in `to_be_verified`:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

The new analysis is a copy of retracted one:

    >>> retest = filter(lambda an: api.get_workflow_status_of(an) == "assigned", references)[0]
    >>> retest.getKeyword() == reference.getKeyword()
    True
    >>> retest.getReferenceAnalysesGroupID() == reference.getReferenceAnalysesGroupID()
    True
    >>> retest.getRetestOf() == reference
    True
    >>> reference.getRetest() == retest
    True
    >>> retest.getAnalysisService() == reference.getAnalysisService()
    True

And keeps the same results as the retracted one:

    >>> retest.getResult() == reference.getResult()
    True

And is located in the same slot as well:

    >>> worksheet.get_slot_position_for(reference) == worksheet.get_slot_position_for(retest)
    True

If I submit the result for the new reference:

    >>> try_transition(retest, "submit", "to_be_verified")
    True

The status of both the reference and the Worksheet is "to_be_verified":

    >>> api.get_workflow_status_of(retest)
    'to_be_verified'
    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'

And I can even retract the retest:

    >>> try_transition(retest, "retract", "retracted")
    True
    >>> api.get_workflow_status_of(retest)
    'retracted'

And one new additional reference has been added in `assigned` state:

    >>> references = worksheet.getReferenceAnalyses()
    >>> sorted(map(api.get_workflow_status_of, references))
    ['assigned', 'retracted', 'retracted']

And the Worksheet has been transitioned to `open`:

    >>> api.get_workflow_status_of(worksheet)
    'open'

Retract transition when reference analyses from same Reference Sample are added
===============================================================================

When analyses from same Reference Sample are added in a worksheet, the
worksheet allocates different slots for them, although each of the slots keeps
the container the analysis belongs to (in this case the same Reference Sample).
Hence, when retracting a reference analysis, the retest must be added in the
same position as the original, regardless of how many reference analyses from
same reference sample exist.
Further information: https://github.com/senaite/senaite.core/pull/1179

Create an Analysis Request:

    >>> ar = new_ar([Cu])
    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    ... for analysis in ar.getAnalyses(full_objects=True):
    ...     worksheet.addAnalysis(analysis)

Add same reference sample twice:

    >>> ref_1 = worksheet.addReferenceAnalyses(control_sample, [api.get_uid(Cu)])[0]
    >>> ref_2 = worksheet.addReferenceAnalyses(control_sample, [api.get_uid(Cu)])[0]
    >>> ref_1 != ref_2
    True

Get the reference analyses positions:

    >>> ref_1_pos = worksheet.get_slot_position_for(ref_1)
    >>> ref_1_pos
    1
    >>> ref_2_pos = worksheet.get_slot_position_for(ref_2)
    >>> ref_2_pos
    2

Submit both:

    >>> ref_1.setResult(12)
    >>> ref_2.setResult(13)
    >>> try_transition(ref_1, "submit", "to_be_verified")
    True
    >>> try_transition(ref_2, "submit", "to_be_verified")
    True

Retract the first reference analysis. The retest has been added in same slot:

    >>> try_transition(ref_1, "retract", "retracted")
    True
    >>> retest_1 = ref_1.getRetest()
    >>> worksheet.get_slot_position_for(retest_1)
    1

And the same if we retract the second reference analysis:

    >>> try_transition(ref_2, "retract", "retracted")
    True
    >>> retest_2 = ref_2.getRetest()
    >>> worksheet.get_slot_position_for(retest_2)
    2
