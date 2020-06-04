Worksheet auto-transitions
==========================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowWorksheetAutotransitions


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

If we submit all analyses from the Worksheet except 1:

    >>> analyses = ws.getAnalyses()
    >>> for analysis in analyses[1:]:
    ...     analysis.setResult(12)
    ...     success = do_action_for(analysis, "submit")

The Worksheet remains in "open" status:

    >>> api.get_workflow_status_of(ws)
    'open'

If now we remove the remaining analysis:

    >>> ws.removeAnalysis(analyses[0])

The Worksheet is submitted automatically because all analyses it contains have
been submitted already:

    >>> api.get_workflow_status_of(ws)
    'to_be_verified'

If we add the analysis again:

    >>> ws.addAnalysis(analyses[0])

The worksheet is rolled-back to open again:

    >>> api.get_workflow_status_of(ws)
    'open'

If we remove again the analysis and verify the rest:

    >>> ws.removeAnalysis(analyses[0])
    >>> api.get_workflow_status_of(ws)
    'to_be_verified'

    >>> setup.setSelfVerificationEnabled(True)
    >>> for analysis in analyses[1:]:
    ...     success = do_action_for(analysis, "verify")
    >>> setup.setSelfVerificationEnabled(False)

The worksheet is verified automatically too:

    >>> api.get_workflow_status_of(ws)
    'verified'

And we cannot add analyses anymore:

    >>> ws.addAnalysis(analyses[0])
    >>> api.get_workflow_status_of(ws)
    'verified'

    >>> not analyses[0].getWorksheet()
    True

    >>> analyses[0] in ws.getAnalyses()
    False
