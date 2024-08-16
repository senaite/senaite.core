    Analysis Turnaround Time For Zero Values
------------------------

Running this test from the buildout directory::

    bin/test test_textual_doctests -t AnalysisTurnaroundTimeForZeroValues


Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor
    >>> from DateTime import DateTime
    >>> from datetime import timedelta
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> from senaite.core.api.dtime import to_DT, to_dt

Functional Helpers:

    >>> def change_receive_date(ar, days):
    ...     prev_date = ar.getDateReceived()
    ...     ar.Schema().getField('DateReceived').set(ar, prev_date + days)
    ...     for analysis in ar.getAnalyses(full_objects=True):
    ...         an_created = analysis.created()
    ...         analysis.getField('creation_date').set(analysis, an_created + days)

    >>> def compute_due_date(analysis):
    ...     start = to_dt(analysis.getStartProcessDate())
    ...     tat = api.to_minutes(**analysis.getMaxTimeAllowed())
    ...     due_date = start + timedelta(minutes=tat)
    ...     return to_DT(due_date)

    >>> def compute_duration(date_from, date_to):
    ...     return (date_to - date_from) * 24 * 60

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = portal.bika_setup

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), DuplicateVariation="0.5")
    >>> service_uids = [api.get_uid(an) for an in [Cu]]
    >>> sampletype_uid = api.get_uid(sampletype)

Set different Turnaround Times for every single Analysis Service:

    >>> Cu.setMaxTimeAllowed(dict(days=0, hours=0, minutes=0))
    >>> maxtime = Cu.getMaxTimeAllowed()
    >>> [maxtime.get("days"), maxtime.get("hours"), maxtime.get("minutes")]
    [0, 0, 0]


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
    ['Cu']
    >>> analyses_dict = {an.getKeyword(): an for an in analyses}


Test basic functions related with TAT
.....................................

Since we haven't received the Analysis Request yet, the duration (time in
minutes taken for analyses must be zero):

    >>> map(lambda an: an.getStartProcessDate(), analyses)
    [None]

    >>> map(lambda an: an.getDuration(), analyses)
    [0]

So Due Date returns empty:

    >>> map(lambda an: an.getDueDate(), analyses)
    [None]

And none of the analyses are late:

    >>> map(lambda an: an.isLateAnalysis(), analyses)
    [False]

And Earliness (in minutes) matches with the TAT assigned to each analysis:

    >>> map(lambda an: api.to_minutes(**an.getMaxTimeAllowed()), analyses)
    [0]
    >>> map(lambda an: an.getEarliness(), analyses)
    [0]

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
......................................

We manually force a receive date 2d before so we can test:

    >>> new_received = map(lambda rec: rec-2, received)
    >>> change_receive_date(ar, -2)
    >>> received = map(lambda an: an.getDateReceived(), analyses)
    >>> start_process = map(lambda an: an.getStartProcessDate(), analyses)
    >>> new_received == received == start_process
    True

Analyses Cu is not late because the Turnaround Time is zero:

    >>> map(lambda an: an.isLateAnalysis(), analyses)
    [False]

Check Due Dates:

    >>> expected_due_dates = map(lambda an: compute_due_date(an), analyses)
    >>> due_dates = map(lambda an: an.getDueDate(), analyses)
    >>> due_dates == expected_due_dates
    False

And duration:

    >>> expected = map(lambda an: int(compute_duration(an.getStartProcessDate(), DateTime())), analyses)
    >>> durations = map(lambda an: int(an.getDuration()), analyses)
    >>> expected == durations
    True

Earliness in minutes. Note the value for Cu is 0 (Turnaround Time set to 0 days, 0 hours, 0 minutes):

    >>> map(lambda an: int(round(an.getEarliness())), analyses)
    [0]

Lateness in minutes. Note that Cu has a value of 0:

    >>> map(lambda an: int(round(an.getLateness())), analyses)
    [0]

Because the analyses (Cu) is not late, the Analysis Request is not late:

    >>> ar.getLate()
    False
