Analysis verification guard and event
=====================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowAnalysisVerify


Test Setup
----------

Needed Imports:

    >>> import transaction
    >>> from DateTime import DateTime
    >>> from plone import api as ploneapi

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for


Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

Needed Imports:

    >>> import re
    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.content.analysisrequest import AnalysisRequest
    >>> from bika.lims.content.sample import Sample
    >>> from bika.lims.content.samplepartition import SamplePartition
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.sample import create_sample
    >>> from bika.lims.utils import tmpID
    >>> from bika.lims.workflow import doActionFor
    >>> from bika.lims.workflow import getCurrentState
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from DateTime import DateTime
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from plone.app.testing import setRoles

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)
    ...
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
    ...
    >>> def try_transition(object, transition_id, target_state_id):
    ...      success = do_action_for(object, transition_id)[0]
    ...      state = api.get_workflow_status_of(object)
    ...      return success and state == target_state_id
    ...
    >>> def submit_analyses(ar):
    ...     for analysis in ar.getAnalyses(full_objects=True):
    ...         analysis.setResult(13)
    ...         do_action_for(analysis, "submit")
    ...

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


Verify transition and guard basic constraints
---------------------------------------------

Create an Analysis Request and submit results:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> submit_analyses(ar)

The status of the Analysis Request and its analyses is `to_be_verified`:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> map(api.get_workflow_status_of, analyses)
    ['to_be_verified', 'to_be_verified', 'to_be_verified']

I cannot verify the analyses because I am the same user who submitted them:

    >>> try_transition(analyses[0], "verify", "verified")
    False
    >>> api.get_workflow_status_of(analyses[0])
    'to_be_verified'

    >>> try_transition(analyses[1], "verify", "verified")
    False
    >>> api.get_workflow_status_of(analyses[1])
    'to_be_verified'

    >>> try_transition(analyses[2], "verify", "verified")
    False
    >>> api.get_workflow_status_of(analyses[2])
    'to_be_verified'

And I cannot verify Analysis Request neither, because the Analysis Request can
only be verified once all the analyses it contains are verified (and this is
done automatically):

    >>> try_transition(ar, "verify", "verified")
    False
    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

But if enable the self verification:

    >>> bikasetup.setSelfVerificationEnabled(True)
    >>> bikasetup.getSelfVerificationEnabled()
    True

Then, I will be able to verify my own results:

    >>> try_transition(analyses[0], "verify", "verified")
    True
    >>> try_transition(analyses[1], "verify", "verified")
    True

But the Analysis Request will remain in `to_be_verified` state:

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

Until we verify all the analyses it contains:

    >>> try_transition(analyses[2], "verify", "verified")
    True
    >>> api.get_workflow_status_of(ar)
    'verified'

To ensure consistency amongst tests, we disable self-verification:

    >>> bikasetup.setSelfVerificationEnabled(False)
    >>> bikasetup.getSelfVerificationEnabled()
    False
