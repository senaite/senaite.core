Analysis unassign guard and event
=================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowAnalysisUnassign


Test Setup
----------

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
    >>> from bika.lims.catalog import CATALOG_WORKSHEET_LISTING
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

    >>> def to_new_worksheet_with_duplicate(ar):
    ...     worksheet = api.create(portal.worksheets, "Worksheet")
    ...     for analysis in ar.getAnalyses(full_objects=True):
    ...         worksheet.addAnalysis(analysis)
    ...     worksheet.addDuplicateAnalyses(1)
    ...     return worksheet

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


Unassign transition and guard basic constraints
-----------------------------------------------

Create an Analysis Request:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> transitioned = do_action_for(ar, "receive")

The status of the analyses is `unassigned`:

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> map(api.get_workflow_status_of, analyses)
    ['unassigned', 'unassigned', 'unassigned']

And the Analysis Request' assigned state index is 'unassigned':

    >>> query = dict(assigned_state='unassigned', UID=api.get_uid(ar))
    >>> len(api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING))
    1
    >>> query = dict(assigned_state='assigned', UID=api.get_uid(ar))
    >>> len(api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING))
    0

Create a Worksheet and add the analyses:

    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> for analysis in analyses:
    ...     worksheet.addAnalysis(analysis)
    >>> sorted((map(lambda an: an.getKeyword(), worksheet.getAnalyses())))
    ['Au', 'Cu', 'Fe']
    >>> map(api.get_workflow_status_of, analyses)
    ['assigned', 'assigned', 'assigned']

The Analysis Request' assigned state indexer is 'assigned':

    >>> query = dict(assigned_state='unassigned', UID=api.get_uid(ar))
    >>> len(api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING))
    0
    >>> query = dict(assigned_state='assigned', UID=api.get_uid(ar))
    >>> len(api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING))
    1

The worksheet has now 3 analyses assigned:

    >>> worksheet.getNumberOfRegularAnalyses()
    3
    >>> worksheet.getNumberOfQCAnalyses()
    0

And metadata gets updated accordingly:

    >>> query = dict(UID=api.get_uid(worksheet))
    >>> ws_brain = api.search(query, CATALOG_WORKSHEET_LISTING)[0]
    >>> ws_brain.getNumberOfRegularAnalyses
    3
    >>> ws_brain.getNumberOfQCAnalyses
    0
    >>> an_uids = sorted(map(api.get_uid, worksheet.getAnalyses()))
    >>> sorted(ws_brain.getAnalysesUIDs) == an_uids
    True

When we unassign the `Cu` analysis, the workseet gets updated:

    >>> cu = filter(lambda an: an.getKeyword() == 'Cu', worksheet.getAnalyses())[0]
    >>> succeed = do_action_for(cu, "unassign")
    >>> api.get_workflow_status_of(cu)
    'unassigned'
    >>> cu in worksheet.getAnalyses()
    False
    >>> worksheet.getNumberOfRegularAnalyses()
    2
    >>> ws_brain = api.search(query, CATALOG_WORKSHEET_LISTING)[0]
    >>> ws_brain.getNumberOfRegularAnalyses
    2
    >>> api.get_uid(cu) in ws_brain.getAnalysesUIDs
    False
    >>> len(ws_brain.getAnalysesUIDs)
    2

And the Analysis Request' assigned state index is updated as well:

    >>> query = dict(assigned_state='unassigned', UID=api.get_uid(ar))
    >>> len(api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING))
    1
    >>> query = dict(assigned_state='assigned', UID=api.get_uid(ar))
    >>> len(api.search(query, CATALOG_ANALYSIS_REQUEST_LISTING))
    0


Unassign of an analysis causes the duplicates to be removed
-----------------------------------------------------------

When the analysis a duplicate comes from is unassigned, the duplicate is
removed from the worksheet too.

Create a Worksheet and add the analyses:

    >>> ar = new_ar([Cu])
    >>> transitioned = do_action_for(ar, "receive")
    >>> worksheet = to_new_worksheet_with_duplicate(ar)
    >>> api.get_workflow_status_of(worksheet)
    'open'
    >>> cu = ar.getAnalyses(full_objects=True)[0]
    >>> dcu = worksheet.getDuplicateAnalyses()[0]

When the analysis `Cu` is unassigned, the duplicate is removed:

    >>> dcu_uid = api.get_uid(dcu)
    >>> try_transition(cu, "unassign", "unassigned")
    True
    >>> api.get_workflow_status_of(cu)
    'unassigned'
    >>> dcu_uid in worksheet.getDuplicateAnalyses()
    False
    >>> api.get_object_by_uid(dcu_uid, None) is None
    True
