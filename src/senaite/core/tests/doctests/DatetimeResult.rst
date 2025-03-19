Datetime Result
---------------

An analysis can be configured so the captured value is treated as a datetime.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t DatetimeResult


Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from datetime import date
    >>> from datetime import datetime
    >>> from DateTime import DateTime

Test fixture:

    >>> import os
    >>> os.environ["TZ"] = "CET"

Functional Helpers:

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

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = api.get_bika_setup()
    >>> date_now = DateTime().strftime("%Y-%m-%d")

Setup the test user
...................

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager.

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])

Setup the initial data
......................

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Faeces", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Microbiology", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Incubations", Department=department)
    >>> Inc = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Incubation", Keyword="Inc", Category=category.UID())
    >>> Inc.setResultType("datetime")

Test datetime result
....................

When a result is captured and the analysis has the value 'datetime' as
`ResultType`, the system stores the value in ISO format:

    >>> sample = new_sample([Inc])

    >>> inc = get_analysis(sample, Inc)
    >>> inc.setResult("2025-03-14 12:56:02")
    >>> inc.getResult()
    '2025-03-14 12:56:02'

    >>> inc.setResult(DateTime(2025, 3, 14, 12, 56, 3))
    >>> inc.getResult()
    '2025-03-14 12:56:03'

    >>> inc.setResult(datetime(2025, 3, 14, 12, 56, 4))
    >>> inc.getResult()
    '2025-03-14 12:56:04'

    >>> inc.setResult(date(2025, 3, 14))
    >>> inc.getResult()
    '2025-03-14 00:00:00'

    >>> inc.setResult("20250314125605")
    >>> inc.getResult()
    '2025-03-14 12:56:05'

Dates without time are supported as well:

    >>> inc.setResult("20250314")
    >>> inc.getResult()
    '2025-03-14 00:00:00'

    >>> inc.setResult(DateTime(2025, 3, 15))
    >>> inc.getResult()
    '2025-03-15 00:00:00'

    >>> inc.setResult(datetime(2025, 3, 16))
    >>> inc.getResult()
    '2025-03-16 00:00:00'

It does store an empty value if not a valid datetime:

    >>> inc.setResult("uhh")
    >>> inc.getResult()
    ''

The function `getFormattedResult` returns the datetime as well, but formatted
in accordance with current locale:

    >>> from senaite.core.api import dtime
    >>> from senaite.core.i18n import get_dt_format

    >>> get_dt_format("datetime")
    '${Y}-${m}-${d} ${H}:${M}'

    >>> inc.setResult("20250314125605")
    >>> inc.getResult()
    '2025-03-14 12:56:05'

    >>> inc.getFormattedResult()
    '2025-03-14 12:56'

    >>> inc.setResult("20250314")
    >>> inc.getResult()
    '2025-03-14 00:00:00'

    >>> inc.getFormattedResult()
    '2025-03-14 00:00'


Test date result
................

When a result is captured and the analysis has the value 'date' as
`ResultType`, the system stores the date without time in ISO format:

    >>> Inc.setResultType("date")
    >>> sample = new_sample([Inc])

    >>> inc = get_analysis(sample, Inc)
    >>> inc.setResult("2025-03-14 12:56:02")
    >>> inc.getResult()
    '2025-03-14'

    >>> inc.setResult(DateTime(2025, 3, 14, 12, 56, 3))
    >>> inc.getResult()
    '2025-03-14'

    >>> inc.setResult(datetime(2025, 3, 14, 12, 56, 4))
    >>> inc.getResult()
    '2025-03-14'

    >>> inc.setResult(date(2025, 3, 14))
    >>> inc.getResult()
    '2025-03-14'

    >>> inc.setResult("20250314125605")
    >>> inc.getResult()
    '2025-03-14'

    >>> inc.setResult("20250314")
    >>> inc.getResult()
    '2025-03-14'

    >>> inc.setResult(DateTime(2025, 3, 15))
    >>> inc.getResult()
    '2025-03-15'

    >>> inc.setResult(datetime(2025, 3, 16))
    >>> inc.getResult()
    '2025-03-16'

It does store an empty value if not a valid datetime:

    >>> inc.setResult("uhh")
    >>> inc.getResult()
    ''

The function `getFormattedResult` returns the date in current locale:

    >>> from senaite.core.api import dtime
    >>> from senaite.core.i18n import get_dt_format

    >>> inc.setResult("20250314125605")
    >>> inc.getResult()
    '2025-03-14'

    >>> get_dt_format("date")
    '${Y}-${m}-${d}'

    >>> inc.getFormattedResult()
    '2025-03-14'
