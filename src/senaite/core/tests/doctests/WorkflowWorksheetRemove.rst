Worksheet remove guard and event
================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowWorksheetRemove


Test Setup
----------

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from DateTime import DateTime
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD

Functional Helpers:

    >>> def new_ar(services):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': DateTime(),
    ...         'SampleType': sampletype.UID()}
    ...     service_uids = map(api.get_uid, services)
    ...     ar = create_analysisrequest(client, request, values, service_uids)
    ...     do_action_for(ar, "receive")
    ...     return ar

    >>> def get_roles_for_permission(permission, context):
    ...     allowed = set(rolesForPermissionOn(permission, context))
    ...     return sorted(allowed)


Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.bika_setup

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(setup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(setup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(setup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())


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

And is not possible to remove unless empty:

    >>> isTransitionAllowed(ws, "remove")
    False

    >>> for analysis in ws.getAnalyses():
    ...     success = do_action_for(analysis, "unassign")
    >>> isTransitionAllowed(ws, "remove")
    True

If we do "remove", the Worksheet object is deleted:

    >>> container = ws.aq_parent
    >>> len(container.objectValues("Worksheet"))
    1
    >>> success = do_action_for(ws, "remove")
    >>> len(container.objectValues("Worksheet"))
    0

Try now for all possible statuses:

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> cu = filter(lambda an: an.getKeyword() == "Cu", analyses)[0]
    >>> fe = filter(lambda an: an.getKeyword() == "Fe", analyses)[0]
    >>> ws = api.create(portal.worksheets, "Worksheet")
    >>> ws.addAnalysis(cu)
    >>> cu.setResult(12)
    >>> success = do_action_for(cu, "submit")

For `to_be_verified` status:

    >>> api.get_workflow_status_of(ws)
    'to_be_verified'
    >>> isTransitionAllowed(ws, "remove")
    False

For `rejected` status:

    >>> success = do_action_for(ws, "reject")
    >>> api.get_workflow_status_of(ws)
    'rejected'
    >>> isTransitionAllowed(ws, "remove")
    False

For `verified` status:

    >>> setup.setSelfVerificationEnabled(True)
    >>> ws = api.create(portal.worksheets, "Worksheet")
    >>> ws.addAnalysis(fe)
    >>> fe.setResult(12)
    >>> success = do_action_for(fe, "submit")
    >>> verified = do_action_for(fe, "verify")
    >>> api.get_workflow_status_of(ws)
    'verified'
    >>> isTransitionAllowed(ws, "remove")
    False
    >>> setup.setSelfVerificationEnabled(False)


Check permissions for Remove transition
---------------------------------------

Create an empty Worksheet:

    >>> ws = api.create(portal.worksheets, "Worksheet")

The status of the Worksheet is `open`:

    >>> api.get_workflow_status_of(ws)
    'open'

Exactly these roles can remove:

    >>> get_roles_for_permission("senaite.core: Transition: Remove Worksheet", ws)
    ['LabManager', 'Manager']

Current user can remove because has the `LabManager` role:

    >>> isTransitionAllowed(ws, "remove")
    True

Also if the user has the role `Manager`:

    >>> setRoles(portal, TEST_USER_ID, ['Manager',])
    >>> isTransitionAllowed(ws, "remove")
    True

But cannot for other roles:

    >>> other_roles = ['Analyst', 'Authenticated', 'LabClerk', 'Verifier']
    >>> setRoles(portal, TEST_USER_ID, other_roles)
    >>> isTransitionAllowed(ws, "remove")
    False

Reset the roles for current user:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
