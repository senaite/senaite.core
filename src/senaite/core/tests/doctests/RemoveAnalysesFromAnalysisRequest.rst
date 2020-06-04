Removal of Analyses from an Analysis Request
============================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t RemoveAnalysesFromAnalysisRequest


Test Setup
----------

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
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

And set some settings:

    >>> bikasetup.setSelfVerificationEnabled(True)


Remove Analyses from an Analysis Request not yet received
---------------------------------------------------------

Create a new Analysis Request:

    >>> ar = new_ar([Cu, Fe, Au])

And remove two analyses (`Cu` and `Fe`):

    >>> ar.setAnalyses([Au])
    >>> map(lambda an: an.getKeyword(), ar.getAnalyses(full_objects=True))
    ['Au']

And the Analysis Request remains in the same state

    >>> api.get_workflow_status_of(ar)
    'sample_due'


Remove Analyses from an Analysis Request with submitted and verified results
----------------------------------------------------------------------------

Create a new Analysis Request and receive:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> transitioned = do_action_for(ar, "receive")
    >>> transitioned[0]
    True
    >>> api.get_workflow_status_of(ar)
    'sample_received'

Submit results for `Fe`:

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> analysis_fe = filter(lambda an: an.getKeyword() == "Fe", analyses)[0]
    >>> analysis_fe.setResult(12)
    >>> transitioned = do_action_for(analysis_fe, "submit")
    >>> transitioned[0]
    True
    >>> api.get_workflow_status_of(analysis_fe)
    'to_be_verified'

The Analysis Request status is still `sample_received`:

    >>> api.get_workflow_status_of(ar)
    'sample_received'

Submit results for `Au`:

    >>> analysis_au = filter(lambda an: an.getKeyword() == "Au", analyses)[0]
    >>> analysis_au.setResult(14)
    >>> transitioned = do_action_for(analysis_au, "submit")
    >>> transitioned[0]
    True
    >>> api.get_workflow_status_of(analysis_au)
    'to_be_verified'

And verify `Au`:

    >>> transitioned = do_action_for(analysis_au, "verify")
    >>> transitioned[0]
    True
    >>> api.get_workflow_status_of(analysis_au)
    'verified'

Again, the Analysis Request status is still `sample_received`:

    >>> api.get_workflow_status_of(ar)
    'sample_received'

But if we remove the analysis without result (`Cu`), the Analysis Request
transitions to "to_be_verified" because follows `Fe`:

    >>> ar.setAnalyses([Fe, Au])
    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

Analyses which are in the state `to_be_verified` can **not** be removed.
Therefore, if we try to remove the analysis `Fe` (in `to_be_verified` state),
the Analysis Request will stay in `to_be_verified` and the Analysis will still
be assigned:

    >>> ar.setAnalyses([Au])

    >>> analysis_fe in ar.objectValues()
    True

    >>> analysis_au in ar.objectValues()
    True

    >>> api.get_workflow_status_of(ar)
    'to_be_verified'

The only way to remove the `Fe` analysis is to retract it first:

    >>> transitioned = do_action_for(analysis_fe, "retract")
    >>> api.get_workflow_status_of(analysis_fe)
    'retracted'

And if we remove analysis `Fe`, the Analysis Request will follow `Au` analysis
(that is `verified`):

    >>> ar.setAnalyses([Au])
    >>> api.get_workflow_status_of(ar)
    'verified'


Remove Analyses from an Analysis Request with all remaining tests verified
--------------------------------------------------------------------------

Create a new Analysis Request and receive:

    >>> ar = new_ar([Cu, Fe, Au])
    >>> transitioned = do_action_for(ar, "receive")
    >>> transitioned[0]
    True
    >>> api.get_workflow_status_of(ar)
    'sample_received'

Submit and verify results for `Fe`:

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> analysis_fe = filter(lambda an: an.getKeyword() == "Fe", analyses)[0]
    >>> analysis_fe.setResult(12)
    >>> transitioned = do_action_for(analysis_fe, "submit")
    >>> transitioned[0]
    True
    >>> api.get_workflow_status_of(analysis_fe)
    'to_be_verified'
    >>> transitioned = do_action_for(analysis_fe, "verify")
    >>> transitioned[0]
    True
    >>> api.get_workflow_status_of(analysis_fe)
    'verified'

Submit and verify results for `Au`:
    >>> analysis_au = filter(lambda an: an.getKeyword() == "Au", analyses)[0]
    >>> analysis_au.setResult(14)
    >>> transitioned = do_action_for(analysis_au, "submit")
    >>> transitioned[0]
    True
    >>> api.get_workflow_status_of(analysis_au)
    'to_be_verified'
    >>> transitioned = do_action_for(analysis_au, "verify")
    >>> transitioned[0]
    True
    >>> api.get_workflow_status_of(analysis_au)
    'verified'

The Analysis Request status is still `sample_received`:

    >>> api.get_workflow_status_of(ar)
    'sample_received'

But if we remove the analysis without result (`Cu`), the Analysis Request
transitions to "verfied" because follows `Fe` and `Au`:

    >>> ar.setAnalyses([Fe, Au])
    >>> api.get_workflow_status_of(ar)
    'verified'
