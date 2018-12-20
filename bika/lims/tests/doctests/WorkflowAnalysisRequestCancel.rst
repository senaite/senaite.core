Analysis Request cancel guard and event
=======================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowAnalysisRequestCancel


Test Setup
----------

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from bika.lims.workflow import getAllowedTransitions
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


Cancel transition and guard basic constraints
---------------------------------------------

Create an Analysis Request:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> api.get_workflow_status_of(ar)
    'sample_due'

Cancel the Analysis Request:

    >>> transitioned = do_action_for(ar, "cancel")
    >>> api.get_workflow_status_of(ar)
    'cancelled'

And all analyses the Analysis Request contains are cancelled too:

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> map(api.get_workflow_status_of, analyses)
    ['cancelled', 'cancelled', 'cancelled']

At this point, only "reinstate" transition is possible:

    >>> getAllowedTransitions(ar)
    ['reinstate']

When the Analysis Request is reinstated, it status becomes the previous before
the cancellation took place:

    >>> transitioned = do_action_for(ar, "reinstate")
    >>> api.get_workflow_status_of(ar)
    'sample_due'

And the analyses are reinstated too:

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> map(api.get_workflow_status_of, analyses)
    ['unassigned', 'unassigned', 'unassigned']

Receive the Analysis Request:

    >>> transitioned = do_action_for(ar, "receive")
    >>> api.get_workflow_status_of(ar)
    'sample_received'

And we can cancel again:

    >>> transitioned = do_action_for(ar, "cancel")
    >>> api.get_workflow_status_of(ar)
    'cancelled'
    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> map(api.get_workflow_status_of, analyses)
    ['cancelled', 'cancelled', 'cancelled']

And reinstate:

    >>> transitioned = do_action_for(ar, "reinstate")
    >>> api.get_workflow_status_of(ar)
    'sample_received'
    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> map(api.get_workflow_status_of, analyses)
    ['unassigned', 'unassigned', 'unassigned']

Thus, the Analysis Request can be cancelled again:

    >>> isTransitionAllowed(ar, "cancel")
    True

But if we assign an analysis to a worksheet, the cancellation is no longer
possible:

    >>> analysis = analyses[0]
    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> worksheet.addAnalysis(analysis)
    >>> api.get_workflow_status_of(analysis)
    'assigned'
    >>> isTransitionAllowed(ar, "cancel")
    False

But if we unassign the analysis, the transition is possible again:

    >>> worksheet.removeAnalysis(analysis)
    >>> api.get_workflow_status_of(analysis)
    'unassigned'
    >>> isTransitionAllowed(ar, "cancel")
    True

If a result for any given analysis is submitted, the Analysis Request cannot be
transitioned to "cancelled" status:

    >>> analysis.setResult(12)
    >>> transitioned = do_action_for(analysis, "submit")
    >>> api.get_workflow_status_of(analysis)
    'to_be_verified'
    >>> isTransitionAllowed(ar, "cancel")
    False
