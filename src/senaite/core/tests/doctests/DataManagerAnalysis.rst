Analysis Data Manager
---------------------

A data manager is an object adapter to get/set/query data by a name.

It is currently used for to set analyses results and interims from
`senaite.app.listing`.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t DataManagerAnalysis


Test Setup
..........

Needed Imports:

    >>> from operator import methodcaller
    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from DateTime import DateTime
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.analysisrequest import create_partition
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from plone.app.testing import setRoles

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

    >>> def new_sample(services, client, contact, sample_type, date_sampled=None):
    ...     values = {
    ...         'Client': api.get_uid(client),
    ...         'Contact': api.get_uid(contact),
    ...         'DateSampled': date_sampled or DateTime().strftime("%Y-%m-%d"),
    ...         'SampleType': api.get_uid(sample_type),
    ...     }
    ...     service_uids = map(api.get_uid, services)
    ...     sample = create_analysisrequest(client, request, values, service_uids)
    ...     return sample

    >>> def get_analysis_from(sample, service):
    ...     service_uid = api.get_uid(service)
    ...     for analysis in sample.getAnalyses(full_objects=True):
    ...         if analysis.getServiceUID() == service_uid:
    ...             return analysis
    ...     return None

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = api.get_setup()

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(bikasetup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(bikasetup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())


Using the data manager to set analysis results
..............................................

Create a new sample:

    >>> sample = new_sample([Cu, Fe, Au], client, contact, sampletype)
    >>> api.get_workflow_status_of(sample)
    'sample_due'

Receive the sample:

    >>> transitioned = do_action_for(sample, "receive")
    >>> api.get_workflow_status_of(sample)
    'sample_received'

Get the analyses from the sample:

    >>> cu = get_analysis_from(sample, Cu)
    >>> fe = get_analysis_from(sample, Fe)
    >>> au = get_analysis_from(sample, Au)

Get the data manager:

    >>> from senaite.core.interfaces import IDataManager

    >>> cu_dm =  IDataManager(cu)
    >>> cu_dm
    <senaite.core.datamanagers.analysis.RoutineAnalysisDataManager object at 0x...>

Getting the value of a named attribute:

    >>> cu_dm.get("Keyword")
    'Cu'

    >>> cu_dm.get("Result")
    ''

    >>> cu_dm.get("NOTEXISTS")
    Traceback (most recent call last):
    ...
    AttributeError: ...
   
Query a value allows to define a default value:

    >>> cu_dm.query("Keyword", default=False)
    'Cu'

    >>> cu_dm.query("Result", default=False)
    ''

    >>> cu_dm.query("NOTEXISTS", default=False)
    False

Seting a value returns a list of updated objects (important when it comes to dependency calculation):

    >>> cu_dm.set("Result", 123)
    [<Analysis at /plone/clients/client-1/W-0001/Cu>]

    >>> cu_dm.get("Result")
    '123'


Permission check
................

Per default, the permisisons `View` for read and `Modify portal content` for
write operations are checked.

Check if the context can be writable (per default Analyses do not grant `Modify portal content`):

    >>> cu_dm.can_write()
    False

    >>> api.security.grant_permission_for(cu, "Modify portal content", ["LabManager"])

    >>> cu_dm.can_write()
    True

Check if the context is readable:

    >>> cu_dm.can_access()
    True

    >>> api.security.revoke_permission_for(cu, "View", [])

    >>> cu_dm.can_access()
    False


Setting calculation interims
............................

Create a new calculation with interims:

    >>> calc = api.create(bikasetup.bika_calculations, "Calculation", title="Drying Loss Calculation")
    >>> calc.setInterimFields([{"keyword": "SW", "title": "Weight of Sample"}, {"keyword": "DW", "title": "Dry Sample Weight"}])
    >>> calc.setFormula("[DW]/[SW]*100")

    >>> calc.getFormula()
    '[DW]/[SW]*100'

    >>> list(sorted(calc.getInterimFields(), key=lambda i: i.get("keyword")))
    [{'keyword': 'DW', 'value': 0, 'title': 'Dry Sample Weight'}, {'keyword': 'SW', 'value': 0, 'title': 'Weight of Sample'}]

Set the calculation to a new service:

    >>> DRL = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Drying Loss", Keyword="DRL", Price="50", Category=category.UID(), Accredited=True, Calculation=calc)

Create a new sample:

    >>> drl_sample = new_sample([DRL], client, contact, sampletype)

Receive the sample:

    >>> transitioned = do_action_for(drl_sample, "receive")

Get the drying loss analysis:

    >>> drl = get_analysis_from(drl_sample, DRL)

Get the data manager

    >>> drl_dm = IDataManager(drl)
    >>> drl_dm
    <senaite.core.datamanagers.analysis.RoutineAnalysisDataManager object at 0x...>

Set the results:

    >>> drl_dm.set("SW", 50)
    [<Analysis at /plone/clients/client-1/W-0002/DRL>]

    >>> drl_dm.set("DW", 10)
    [<Analysis at /plone/clients/client-1/W-0002/DRL>]


Check if the result was updated:

    >>> drl_dm.get("Result")
    '20.0'
