Analysis publication guard and event
====================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowAnalysisPublish


Test Setup
----------

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import getAllowedTransitions
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

    >>> def try_transition(object, transition_id, target_state_id):
    ...      success = do_action_for(object, transition_id)[0]
    ...      state = api.get_workflow_status_of(object)
    ...      return success and state == target_state_id

    >>> def submit_analyses(ar):
    ...     for analysis in ar.getAnalyses(full_objects=True):
    ...         analysis.setResult(13)
    ...         do_action_for(analysis, "submit")

    >>> def verify_analyses(ar):
    ...     for analysis in ar.getAnalyses(full_objects=True):
    ...         do_action_for(analysis, "verify")

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
    >>> bikasetup.setSelfVerificationEnabled(True)

Publish transition and guard basic constraints
----------------------------------------------

Create an Analysis Request, submit results and verify:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> submit_analyses(ar)
    >>> verify_analyses(ar)
    >>> api.get_workflow_status_of(ar)
    'verified'

I cannot publish the analyses individually:

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> try_transition(analyses[0], "publish", "published")
    False
    >>> api.get_workflow_status_of(analyses[0])
    'verified'

    >>> try_transition(analyses[1], "publish", "published")
    False
    >>> api.get_workflow_status_of(analyses[1])
    'verified'

    >>> try_transition(analyses[2], "publish", "published")
    False
    >>> api.get_workflow_status_of(analyses[2])
    'verified'

But if we publish the Analysis Request, analyses will follow:

    >>> success = do_action_for(ar, "publish")
    >>> api.get_workflow_status_of(ar)
    'published'
    >>> map(api.get_workflow_status_of, analyses)
    ['published', 'published', 'published']


Check permissions for Published state
-------------------------------------

In published state, exactly these roles can view results:

    >>> analysis = ar.getAnalyses(full_objects=True)[0]
    >>> api.get_workflow_status_of(analysis)
    'published'
    >>> get_roles_for_permission("senaite.core: View Results", analysis)
    ['Analyst', 'LabClerk', 'LabManager', 'Manager', 'Owner', 'RegulatoryInspector']

And no transition can be done from this state:

    >>> getAllowedTransitions(analysis)
    []
