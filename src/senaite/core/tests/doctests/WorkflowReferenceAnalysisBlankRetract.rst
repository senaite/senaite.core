Reference Analysis (Blanks) retract guard and event
---------------------------------------------------

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowReferenceAnalysisBlankRetract


Test Setup
..........

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.interfaces import IRetracted
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
    >>> setup = portal.setup
    >>> bikasetup = portal.bika_setup
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(bikasetup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
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
    >>> blank_sample = api.create(supplier, "ReferenceSample", title="Blank",
    ...                    ReferenceDefinition=blank_def,
    ...                    Blank=True, ExpiryDate=date_future,
    ...                    ReferenceResults=blank_refs)


Blank retraction basic constraints
..................................

Create a Worksheet and submit regular analyses:

    >>> ar = new_ar([Cu])
    >>> worksheet = to_new_worksheet_with_reference(ar, blank_sample)
    >>> submit_regular_analyses(worksheet)

Get the blank and submit:

    >>> blank = worksheet.getReferenceAnalyses()[0]
    >>> blank.setResult(0)
    >>> try_transition(blank, "submit", "to_be_verified")
    True
    >>> api.get_workflow_status_of(blank)
    'to_be_verified'

Retract the blank:

    >>> try_transition(blank, "retract", "retracted")
    True
    >>> api.get_workflow_status_of(blank)
    'retracted'

And one new additional blank has been added in `assigned` state:

    >>> references = worksheet.getReferenceAnalyses()
    >>> sorted(map(api.get_workflow_status_of, references))
    ['assigned', 'retracted']

And the Worksheet has been transitioned to `open`:

    >>> api.get_workflow_status_of(worksheet)
    'open'

While the Analysis Request is still in `to_be_verified`:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

The new blank is a copy of retracted one:

    >>> retest = filter(lambda an: api.get_workflow_status_of(an) == "assigned", references)[0]
    >>> retest.getKeyword() == blank.getKeyword()
    True
    >>> retest.getReferenceAnalysesGroupID() == blank.getReferenceAnalysesGroupID()
    True
    >>> retest.getRetestOf() == blank
    True
    >>> blank.getRetest() == retest
    True
    >>> retest.getAnalysisService() == blank.getAnalysisService()
    True

And keeps the same results as the retracted one:

    >>> retest.getResult() == blank.getResult()
    True

And is located in the same slot as well:

    >>> worksheet.get_slot_position_for(blank) == worksheet.get_slot_position_for(retest)
    True

If I submit the result for the new blank:

    >>> try_transition(retest, "submit", "to_be_verified")
    True

The status of both the blank and the Worksheet is "to_be_verified":

    >>> api.get_workflow_status_of(retest)
    'to_be_verified'
    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'

And I can even retract the retest:

    >>> try_transition(retest, "retract", "retracted")
    True
    >>> api.get_workflow_status_of(retest)
    'retracted'

And one new additional blank has been added in `assigned` state:

    >>> references = worksheet.getReferenceAnalyses()
    >>> sorted(map(api.get_workflow_status_of, references))
    ['assigned', 'retracted', 'retracted']

And the Worksheet has been transitioned to `open`:

    >>> api.get_workflow_status_of(worksheet)
    'open'

Retract transition when a duplicate from same Reference Sample is added
-----------------------------------------------------------------------

When analyses from same Reference Sample are added in a worksheet, the
worksheet allocates different slots for them, although each of the slots keeps
the container the blank belongs to (in this case the same Reference Sample).
Hence, when retracting a reference analysis, the retest must be added in the
same position as the original, regardless of how many blanks from same
reference sample exist.
Further information: https://github.com/senaite/senaite.core/pull/1179

Create an Analysis Request:

    >>> ar = new_ar([Cu])
    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    ... for analysis in ar.getAnalyses(full_objects=True):
    ...     worksheet.addAnalysis(analysis)

Add same reference sample twice:

    >>> blank_1 = worksheet.addReferenceAnalyses(blank_sample, [api.get_uid(Cu)])[0]
    >>> blank_2 = worksheet.addReferenceAnalyses(blank_sample, [api.get_uid(Cu)])[0]
    >>> blank_1 != blank_2
    True

Get the reference analyses positions:

    >>> blank_1_pos = worksheet.get_slot_position_for(blank_1)
    >>> blank_1_pos
    1
    >>> blank_2_pos = worksheet.get_slot_position_for(blank_2)
    >>> blank_2_pos
    2

Submit both:

    >>> blank_1.setResult(12)
    >>> blank_2.setResult(13)
    >>> try_transition(blank_1, "submit", "to_be_verified")
    True
    >>> try_transition(blank_2, "submit", "to_be_verified")
    True

Retract the first blank. The retest has been added in same slot:

    >>> try_transition(blank_1, "retract", "retracted")
    True
    >>> retest_1 = blank_1.getRetest()
    >>> worksheet.get_slot_position_for(retest_1)
    1

And the same if we retract the second blank analysis:

    >>> try_transition(blank_2, "retract", "retracted")
    True
    >>> retest_2 = blank_2.getRetest()
    >>> worksheet.get_slot_position_for(retest_2)
    2

IRetracted interface is provided by retracted blanks
....................................................

When retracted, blank analyses are marked with the `IRetracted` interface:

    >>> sample = new_ar([Cu])
    >>> worksheet = to_new_worksheet_with_reference(sample, blank_sample)
    >>> blank = worksheet.getReferenceAnalyses()[0]
    >>> blank.setResult(12)
    >>> success = do_action_for(blank, "submit")
    >>> IRetracted.providedBy(blank)
    False

    >>> success = do_action_for(blank, "retract")
    >>> IRetracted.providedBy(blank)
    True

But the retest does not provide `IRetracted`:

    >>> retest = blank.getRetest()
    >>> IRetracted.providedBy(retest)
    False
