Worksheet retract guard and event
=================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowWorksheetRetract


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
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())
    >>> supplier = api.create(bikasetup.bika_suppliers, "Supplier", Name="Naralabs")
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
    >>> blank = api.create(supplier, "ReferenceSample", title="Blank",
    ...                    ReferenceDefinition=blank_def,
    ...                    Blank=True, ExpiryDate=date_future,
    ...                    ReferenceResults=blank_refs)
    >>> control = api.create(supplier, "ReferenceSample", title="Control",
    ...                      ReferenceDefinition=control_def,
    ...                      Blank=False, ExpiryDate=date_future,
    ...                      ReferenceResults=control_refs)


Retract transition and guard basic constraints
----------------------------------------------

Create a Worksheet:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> ws = api.create(portal.worksheets, "Worksheet")
    >>> for analysis in ar.getAnalyses(full_objects=True):
    ...     ws.addAnalysis(analysis)

The status of the worksheet is "open":

    >>> api.get_workflow_status_of(ws)
    'open'

And is not possible to retract when status is "open":

    >>> isTransitionAllowed(ws, "retract")
    False

But is possible to retract if the status is "to_be_verified":

    >>> submit_analyses(ar)
    >>> list(set(map(api.get_workflow_status_of, ws.getAnalyses())))
    ['to_be_verified']
    >>> api.get_workflow_status_of(ws)
    'to_be_verified'
    >>> isTransitionAllowed(ws, "retract")
    True

The retraction of the worksheet causes all its analyses to be retracted:

    >>> do_action_for(ws, "retract")
    (True, '')
    >>> analyses = ws.getAnalyses()
    >>> len(analyses)
    6
    >>> sorted(map(api.get_workflow_status_of, analyses))
    ['assigned', 'assigned', 'assigned', 'retracted', 'retracted', 'retracted']

And the Worksheet transitions to "open":

    >>> api.get_workflow_status_of(ws)
    'open'

With duplicates and reference analyses, the system behaves the same way:

    >>> dups = ws.addDuplicateAnalyses(1)
    >>> blanks = ws.addReferenceAnalyses(blank, [Cu.UID(), Fe.UID(), Au.UID()])
    >>> controls = ws.addReferenceAnalyses(control, [Cu.UID(), Fe.UID(), Au.UID()])
    >>> len(ws.getAnalyses())
    15
    >>> for analysis in ws.getAnalyses():
    ...     analysis.setResult(10)
    ...     success = do_action_for(analysis, "submit")
    >>> analyses = ws.getAnalyses()
    >>> sorted(set(map(api.get_workflow_status_of, analyses)))
    ['retracted', 'to_be_verified']

Since all non-retracted analyses have been submitted, the worksheet status is
`to_be_verified`:

    >>> api.get_workflow_status_of(ws)
    'to_be_verified'

The Worksheet can be retracted:

    >>> isTransitionAllowed(ws, "retract")
    True
    >>> do_action_for(ws, "retract")
    (True, '')
    >>> analyses = ws.getAnalyses()
    >>> len(analyses)
    27
    >>> statuses = map(api.get_workflow_status_of, analyses)
    >>> len(filter(lambda st: st == "assigned", statuses))
    12
    >>> len(filter(lambda st: st == "retracted", statuses))
    15

And the worksheet transitions to "open":

    >>> api.get_workflow_status_of(ws)
    'open'


Check permissions for Retract transition
----------------------------------------

Create a Worksheet and submit results:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> ws = api.create(portal.worksheets, "Worksheet")
    >>> for analysis in ar.getAnalyses(full_objects=True):
    ...     ws.addAnalysis(analysis)
    >>> submit_analyses(ar)

The status of the Worksheet and its analyses is `to_be_verified`:

    >>> api.get_workflow_status_of(ws)
    'to_be_verified'

    >>> analyses = ws.getAnalyses()
    >>> list(set(map(api.get_workflow_status_of, analyses)))
    ['to_be_verified']

Exactly these roles can retract:

    >>> get_roles_for_permission("senaite.core: Transition: Retract", ws)
    ['LabManager', 'Manager']

Current user can verify because has the `LabManager` role:

    >>> isTransitionAllowed(ws, "retract")
    True

Also if the user has the role `Manager`:

    >>> setRoles(portal, TEST_USER_ID, ['Manager',])
    >>> isTransitionAllowed(ws, "retract")
    True

But cannot for other roles:

    >>> other_roles = ['Analyst', 'Authenticated', 'LabClerk', 'Verifier']
    >>> setRoles(portal, TEST_USER_ID, other_roles)
    >>> isTransitionAllowed(ws, "retract")
    False

Reset the roles for current user:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
