Text Result
-----------

An analysis can be configured so the captured value is treated as text.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t TextResult


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
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID())
    >>> Cu.setResultType("text")

Test text result
................

When a result is captured and the analysis has the value 'text' as ResultType,
the system returns the string value "as-is" without any processing:

    >>> sample = new_sample([Cu])

    >>> cu = get_analysis(sample, Cu)
    >>> cu.setResult(1.23456789)
    >>> cu.getResult()
    '1.23456789'
    >>> cu.getFormattedResult()
    '1.23456789'
    >>> cu.setResult('0')
    >>> cu.getResult()
    '0'
    >>> cu.getFormattedResult()
    '0'

    >>> cu.setResult('This is a text result')
    >>> cu.getResult()
    'This is a text result'
    >>> cu.getFormattedResult()
    'This is a text result'

The result supports multiple lines as well:

    >>> cu.setResult("This is a text result with\r\nof multiple\nlines")
    >>> cu.getResult()
    'This is a text result with\r\nof multiple\nlines'

If the result contains html characters, `getFormattedResult` escape them
by default:

    >>> cu.setResult('< Detection Limit')
    >>> cu.getResult()
    '< Detection Limit'
    >>> cu.getFormattedResult()
    '&lt; Detection Limit'

Unless the parameter `html` is set to False:

    >>> cu.getFormattedResult(html=False)
    '< Detection Limit'
