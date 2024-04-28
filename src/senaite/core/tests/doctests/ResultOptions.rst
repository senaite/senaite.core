Result Options
--------------

An analysis can be configured so a selection list with options are displayed
for selection rather than an input text for manual introduction of a value.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t ResultOptions


Test Setup
..........

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

    >>> def new_sample(services):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': date_now,
    ...         'SampleType': sampletype.UID()}
    ...     service_uids = map(api.get_uid, services)
    ...     ar = create_analysisrequest(client, request, values, service_uids)
    ...     transitioned = do_action_for(ar, "receive")
    ...     return ar

    >>> def get_analysis(sample, service):
    ...     service_uid = api.get_uid(service)
    ...     for analysis in sample.getAnalyses(full_objects=True):
    ...         if analysis.getServiceUID() == service_uid:
    ...             return analysis
    ...     return None

    >>> def submit_analyses(ar, result="13"):
    ...     for analysis in ar.getAnalyses(full_objects=True):
    ...         analysis.setResult(result)
    ...         do_action_for(analysis, "submit")

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = api.get_bika_setup()
    >>> date_now = DateTime().strftime("%Y-%m-%d")

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
    >>> Zn = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Zinc", Keyword="Zn", Price="20", Category=category.UID())

Apply result options to the services:

    >>> options = [
    ...     {"ResultValue": "0", "ResultText": "Zero"},
    ...     {"ResultValue": "1", "ResultText": "One"},
    ...     {"ResultValue": "2", "ResultText": "Two"},
    ...     {"ResultValue": "3", "ResultText": "Three"},
    ... ]
    >>> services = [Cu, Fe, Au, Zn]
    >>> for service in services:
    ...     service.setResultOptions(options)

And a different control type for each service

    >>> Cu.setResultType("select")
    >>> Fe.setResultType("multiselect")
    >>> Au.setResultType("multiselect_duplicates")
    >>> Zn.setResultType("multichoice")

Test formatted result
.....................

The system returns the option text as the formatted result:

    >>> sample = new_sample([Cu, Fe, Au, Zn])

    >>> cu = get_analysis(sample, Cu)
    >>> cu.setResult('0')
    >>> cu.getResult()
    '0'
    >>> cu.getFormattedResult()
    'Zero'

    >>> fe = get_analysis(sample, Fe)
    >>> fe.setResult(['0', '1'])
    >>> fe.getResult()
    '["0", "1"]'
    >>> fe.getFormattedResult()
    'Zero<br/>One'

    >>> au = get_analysis(sample, Au)
    >>> au.setResult(['0', '1', '1'])
    >>> au.getResult()
    '["0", "1", "1"]'
    >>> au.getFormattedResult()
    'Zero<br/>One<br/>One'

    >>> zn = get_analysis(sample, Zn)
    >>> zn.setResult(['0', '1'])
    >>> zn.getResult()
    '["0", "1"]'
    >>> zn.getFormattedResult()
    'Zero<br/>One'

Even if the analysis has the "String result" setting enabled:

    >>> analyses = [cu, fe, au, zn]
    >>> for analysis in analyses:
    ...     analysis.setStringResult(True)

    >>> cu.getFormattedResult()
    'Zero'
    >>> fe.getFormattedResult()
    'Zero<br/>One'
    >>> au.getFormattedResult()
    'Zero<br/>One<br/>One'
    >>> zn.getFormattedResult()
    'Zero<br/>One'
