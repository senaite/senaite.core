Analysis Turnaround Time
========================

Running this test from the buildout directory::

    bin/test test_textual_doctests -t AnalysisTurnaroundTime


Test Setup
----------

Needed Imports:

    >>> import re
    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.api.analysis import get_formatted_interval
    >>> from bika.lims.api.analysis import is_out_of_range
    >>> from bika.lims.content.analysisrequest import AnalysisRequest
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils import tmpID
    >>> from bika.lims.workflow import doActionFor
    >>> from bika.lims.workflow import getCurrentState
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from bika.lims.workflow import getReviewHistory
    >>> from DateTime import DateTime
    >>> from datetime import timedelta
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from plone.app.testing import setRoles
    >>> from Products.ATContentTypes.utils import DT2dt, dt2DT

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def change_receive_date(ar, days):
    ...     prev_date = ar.getDateReceived()
    ...     ar.Schema().getField('DateReceived').set(ar, prev_date + days)
    ...     for analysis in ar.getAnalyses(full_objects=True):
    ...         an_created = analysis.created()
    ...         analysis.getField('creation_date').set(analysis, an_created + days)

    >>> def compute_due_date(analysis):
    ...     start = DT2dt(analysis.getStartProcessDate())
    ...     tat = api.to_minutes(**analysis.getMaxTimeAllowed())
    ...     due_date = start + timedelta(minutes=tat)
    ...     return dt2DT(due_date)

    >>> def compute_duration(date_from, date_to):
    ...     return (date_to - date_from) * 24 * 60

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> bikasetup = portal.bika_setup

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(bikasetup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(bikasetup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(bikasetup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), DuplicateVariation="0.5")
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID(), DuplicateVariation="0.5")
    >>> Au = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID(), DuplicateVariation="0.5")
    >>> Mg = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Magnesium", Keyword="Mg", Price="20", Category=category.UID(), DuplicateVariation="0.5")
    >>> service_uids = [api.get_uid(an) for an in [Cu, Fe, Au, Mg]]
    >>> sampletype_uid = api.get_uid(sampletype)

Set different Turnaround Times for every single Analysis Service:

    >>> Au.setMaxTimeAllowed(dict(days=2, hours=8, minutes=30))
    >>> maxtime = Au.getMaxTimeAllowed()
    >>> [maxtime.get("days"), maxtime.get("hours"), maxtime.get("minutes")]
    [2, 8, 30]

    >>> Cu.setMaxTimeAllowed(dict(days=1, hours=4, minutes=0))
    >>> maxtime = Cu.getMaxTimeAllowed()
    >>> [maxtime.get("days"), maxtime.get("hours"), maxtime.get("minutes")]
    [1, 4, 0]

    >>> Fe.setMaxTimeAllowed(dict(days=3, hours=0, minutes=0))
    >>> maxtime = Fe.getMaxTimeAllowed()
    >>> [maxtime.get("days"), maxtime.get("hours"), maxtime.get("minutes")]
    [3, 0, 0]

And leave Magnesium (Mg) without any Turnaround Time set, so it will use the
default Turnaround time set in setup:

    >>> maxtime = bikasetup.getDefaultTurnaroundTime()
    >>> [maxtime.get("days"), maxtime.get("hours"), maxtime.get("minutes")]
    [5, 0, 0]

    >>> maxtime = Mg.getMaxTimeAllowed()
    >>> [maxtime.get("days"), maxtime.get("hours"), maxtime.get("minutes")]
    [5, 0, 0]

Create an Analysis Request:

    >>> values = {
    ...     'Client': api.get_uid(client),
    ...     'Contact': api.get_uid(contact),
    ...     'DateSampled': date_now,
    ...     'SampleType': sampletype_uid,
    ...     'Priority': '1',
    ... }

    >>> ar = create_analysisrequest(client, request, values, service_uids)

Get the Analyses for further use:

    >>> analyses = ar.getAnalyses(full_objects=True)
    >>> analyses = sorted(analyses, key=lambda an: an.getKeyword())
    >>> map(lambda an: an.getKeyword(), analyses)
    ['Au', 'Cu', 'Fe', 'Mg']
    >>> analyses_dict = {an.getKeyword(): an for an in analyses}


Test basic functions related with TAT
-------------------------------------

Since we haven't received the Analysis Request yet, the duration (time in
minutes taken for analyses must be zero):

    >>> map(lambda an: an.getStartProcessDate(), analyses)
    [None, None, None, None]

    >>> map(lambda an: an.getDuration(), analyses)
    [0, 0, 0, 0]

So Due Date returns empty:

    >>> map(lambda an: an.getDueDate(), analyses)
    [None, None, None, None]

And none of the analyses are late:

    >>> map(lambda an: an.isLateAnalysis(), analyses)
    [False, False, False, False]

And Earliness (in minutes) matches with the TAT assigned to each analysis:

    >>> map(lambda an: api.to_minutes(**an.getMaxTimeAllowed()), analyses)
    [3390, 1680, 4320, 7200]
    >>> map(lambda an: an.getEarliness(), analyses)
    [3390, 1680, 4320, 7200]

Receive the Analysis Request:

    >>> success = doActionFor(ar, 'receive')

The process date now for analyses is the received date:

    >>> start_process = map(lambda an: an.getStartProcessDate(), analyses)
    >>> received = map(lambda an: an.getDateReceived(), analyses)
    >>> received == start_process
    True

Also, the Analysis Request is not late because none of its analyses is late:

    >>> ar.getLate()
    False


Test TAT with analyses received 2d ago
--------------------------------------

We manually force a receive date 2d before so we can test:

    >>> new_received = map(lambda rec: rec-2, received)
    >>> change_receive_date(ar, -2)
    >>> received = map(lambda an: an.getDateReceived(), analyses)
    >>> start_process = map(lambda an: an.getStartProcessDate(), analyses)
    >>> new_received == received == start_process
    True

Analyses Au and Fe are not late, but Cu is late:

    >>> map(lambda an: an.isLateAnalysis(), analyses)
    [False, True, False, False]

Check Due Dates:

    >>> expected_due_dates = map(lambda an: compute_due_date(an), analyses)
    >>> due_dates = map(lambda an: an.getDueDate(), analyses)
    >>> due_dates == expected_due_dates
    True

And duration:

    >>> expected = map(lambda an: int(compute_duration(an.getStartProcessDate(), DateTime())), analyses)
    >>> durations = map(lambda an: int(an.getDuration()), analyses)
    >>> expected == durations
    True

Earliness in minutes. Note the value for Cu is negative (is late), and the value
for Mg is 0 (no Turnaround Time) set:

    >>> map(lambda an: int(round(an.getEarliness())), analyses)
    [510, -1200, 1440, 4320]

Lateness in minutes. Note that all values are negative except for Cu:

    >>> map(lambda an: int(round(an.getLateness())), analyses)
    [-510, 1200, -1440, -4320]

Because one of the analyses (Cu) is late, the Analysis Request is late too:

    >>> ar.getLate()
    True
