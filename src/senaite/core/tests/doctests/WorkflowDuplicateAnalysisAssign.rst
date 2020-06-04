Duplicate Analysis assign guard and event
=========================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowDuplicateAnalysisAssign


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
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())


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

Add duplicate analyses from the analyses in position 1

    >>> duplicates = worksheet.addDuplicateAnalyses(1)
    >>> len(duplicates)
    3

The status of the duplicates is `assigned`:

    >>> duplicates = worksheet.getDuplicateAnalyses()
    >>> map(api.get_workflow_status_of, duplicates)
    ['assigned', 'assigned', 'assigned']

And are associated to the worksheet:

    >>> wuid = list(set(map(lambda dup: dup.getWorksheetUID(), duplicates)))
    >>> len(wuid)
    1
    >>> wuid[0] == api.get_uid(worksheet)
    True

Duplicates do not have an Analyst assigned, though:

    >>> list(set(map(lambda dup: dup.getAnalyst(), duplicates)))
    ['']

If I assign a user to the Worksheet, same user will be assigned to analyses:

    >>> worksheet.setAnalyst(TEST_USER_ID)
    >>> worksheet.getAnalyst() == TEST_USER_ID
    True

    >>> filter(lambda an: an.getAnalyst() != TEST_USER_ID, analyses)
    []

And to the duplicates as well:

    >>> filter(lambda an: an.getAnalyst() != TEST_USER_ID, duplicates)
    []

I can remove one of the duplicates from the Worksheet:

    >>> duplicate = duplicates[0]
    >>> dup_uid = api.get_uid(duplicate)
    >>> worksheet.removeAnalysis(duplicate)
    >>> len(worksheet.getDuplicateAnalyses())
    2

And the removed duplicate no longer exists:

    >>> api.get_object_by_uid(dup_uid, None) is None
    True

We add again duplicates for same analyses from slot 1 to slot 2:

    >>> dup_uids = map(api.get_uid, worksheet.getDuplicateAnalyses())
    >>> duplicates = worksheet.addDuplicateAnalyses(1, 2)

Since there is only one duplicate analysis missing in slot 2 (that we removed
earlier), only one duplicate analysis is added:

    >>> len(duplicates)
    1
    >>> len(worksheet.getDuplicateAnalyses())
    3
    >>> len(filter(lambda dup: dup in duplicates, worksheet.getDuplicateAnalyses()))
    1

And since the worksheet has an Analyst already assigned, duplicates too:

    >>> filter(lambda an: an.getAnalyst() != TEST_USER_ID, duplicates)
    []

From `assigned` state I can do submit:

    >>> duplicates = worksheet.getDuplicateAnalyses()
    >>> map(api.get_workflow_status_of, duplicates)
    ['assigned', 'assigned', 'assigned']
    >>> duplicates[0].setResult(20)
    >>> duplicates[1].setResult(23)
    >>> try_transition(duplicates[0], "submit", "to_be_verified")
    True
    >>> try_transition(duplicates[1], "submit", "to_be_verified")
    True

And duplicates transition to `to_be_verified`:

    >>> map(api.get_workflow_status_of, duplicates)
    ['to_be_verified', 'to_be_verified', 'assigned']

While keeping the Analyst that was assigned to the worksheet:

    >>> filter(lambda an: an.getAnalyst() != TEST_USER_ID, duplicates)
    []

And since there is still regular analyses in the Worksheet not yet submitted,
the Worksheet remains in `open` state:

    >>> api.get_workflow_status_of(worksheet)
    'open'

Duplicates get removed when I unassign the analyses they come from:

    >>> duplicate = duplicates[0]
    >>> analysis = duplicate.getAnalysis()
    >>> dup_uid = api.get_uid(duplicate)
    >>> an_uid = api.get_uid(analysis)
    >>> worksheet.removeAnalysis(analysis)
    >>> api.get_workflow_status_of(analysis)
    'unassigned'
    >>> filter(lambda an: api.get_uid(an) == an_uid, worksheet.getAnalyses())
    []
    >>> filter(lambda dup: api.get_uid(dup.getAnalysis()) == an_uid, worksheet.getDuplicateAnalyses())
    []
    >>> len(worksheet.getDuplicateAnalyses())
    2
    >>> api.get_object_by_uid(dup_uid, None) is None
    True

I submit the results for the rest of analyses:

    >>> for analysis in worksheet.getRegularAnalyses():
    ...     analysis.setResult(10)
    ...     transitioned = do_action_for(analysis, "submit")
    >>> map(api.get_workflow_status_of, worksheet.getRegularAnalyses())
    ['to_be_verified', 'to_be_verified']

And since there is a duplicate that has not been yet submitted, the Worksheet
remains in `open` state:

    >>> duplicates = worksheet.getDuplicateAnalyses()
    >>> duplicate = filter(lambda dup: api.get_workflow_status_of(dup) == "assigned", duplicates)
    >>> len(duplicate)
    1
    >>> duplicate = duplicate[0]
    >>> api.get_workflow_status_of(duplicate)
    'assigned'
    >>> api.get_workflow_status_of(worksheet)
    'open'

But if I remove the duplicate analysis that has not been yet submitted, the
status of the Worksheet is promoted to `to_be_verified`, cause all the rest
are in `to_be_verified` state:

    >>> dup_uid = api.get_uid(duplicate)
    >>> worksheet.removeAnalysis(duplicate)
    >>> len(worksheet.getDuplicateAnalyses())
    1
    >>> api.get_object_by_uid(dup_uid, None) is None
    True
    >>> api.get_workflow_status_of(worksheet)
    'to_be_verified'

And now, I cannot add duplicates anymore:

    >>> worksheet.addDuplicateAnalyses(1)
    []
    >>> len(worksheet.getDuplicateAnalyses())
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

Add a Duplicate analysis of the analysis in position 1:

    >>> len(worksheet.addDuplicateAnalyses(1))
    3

Since a duplicate can only live inside a Worksheet, the initial state of the
duplicate is `assigned` by default:

    >>> duplicates = worksheet.getDuplicateAnalyses()
    >>> map(api.get_workflow_status_of, duplicates)
    ['assigned', 'assigned', 'assigned']
