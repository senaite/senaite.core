Duplicate results range
=======================

The valid result range for a duplicate analysis is calculated by applying a
duplicate variation percentage to the result from the original analysis. If the
analysis has result options enabled or string results enabled, results from
both duplicate and original analysis must match 100%.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t DuplicateResultsRange

Test Setup
----------

Needed imports:

    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from bika.lims import api
    >>> from bika.lims.api.analysis import is_out_of_range
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for

Functional Helpers:

    >>> def new_sample(services):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': DateTime().strftime("%Y-%m-%d"),
    ...         'SampleType': sampletype.UID()}
    ...     service_uids = map(api.get_uid, services)
    ...     ar = create_analysisrequest(client, request, values, service_uids)
    ...     transitioned = do_action_for(ar, "receive")
    ...     return ar

    >>> def new_worksheet(analyses):
    ...     analyses = []
    ...     for num in range(num_analyses):
    ...         sample = new_sample(analyses)
    ...         analyses.extend(sample.getAnalyses(full_objects=True))
    ...     worksheet = api.create(portal.worksheets, "Worksheet")
    ...     worksheet.addAnalyses(analyses)
    ...     return worksheet

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_setup()

Create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['Manager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(setup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID())
    >>> Fe = api.create(setup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(setup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())


Duplicate of an analysis with numeric result
--------------------------------------------

Set the duplicate variation in percentage for `Cu`:

    >>> Cu.setDuplicateVariation("10")
    >>> Cu.getDuplicateVariation()
    '10.00'

Create a Sample and receive:

    >>> sample = new_sample([Cu])

Create a worksheet and assign the analyses:

    >>> analyses = sample.getAnalyses(full_objects=True)
    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> worksheet.addAnalyses(analyses)

Add a duplicate for analysis `Cu`:

    >>> worksheet.addDuplicateAnalyses(1)
    [<DuplicateAnalysis at /plone/worksheets/WS-001/...

    >>> duplicate = worksheet.getDuplicateAnalyses()[0]
    >>> duplicate.getAnalysis()
    <Analysis at /plone/clients/client-1/W-0001/Cu>

    >>> duplicate.getResultsRange()
    {}

Set a result of 50 for the original analysis `Cu`:

    >>> cu = analyses[0]
    >>> cu.setResult(50)
    >>> duplicate.getAnalysis().getResult()
    '50'

    >>> result_range = duplicate.getResultsRange()
    >>> (result_range.min, result_range.max)
    ('45.0', '55.0')

We can set a result for the duplicate within the range:

    >>> duplicate.setResult(47)
    >>> is_out_of_range(duplicate)
    (False, False)

Or an out-of-range result:

    >>> duplicate.setResult(42)
    >>> is_out_of_range(duplicate)
    (True, True)

We can do same exercise, but the other way round. We can submit the result for
the duplicate first:

    >>> sample = new_sample([Cu])
    >>> cu = sample.getAnalyses(full_objects=True)[0]
    >>> worksheet.addAnalyses([cu])

We add a duplicate for new analysis, that is located at slot number 3:

    >>> worksheet.addDuplicateAnalyses(src_slot=3)
    [<DuplicateAnalysis at /plone/worksheets/WS-001/...

    >>> duplicate = worksheet.getDuplicateAnalyses()
    >>> duplicate = filter(lambda dup: dup.getAnalysis() == cu, duplicate)[0]
    >>> duplicate.getAnalysis()
    <Analysis at /plone/clients/client-1/W-0002/Cu>

    >>> duplicate.getResultsRange()
    {}

We set the result for the duplicate first, but it does not have a valid
result range because the original analysis has no result yet:

    >>> duplicate.setResult(58)
    >>> duplicate.getResultsRange()
    {}

    >>> is_out_of_range(duplicate)
    (False, False)

    >>> cu.setResult(50)
    >>> result_range = duplicate.getResultsRange()
    >>> (result_range.min, result_range.max)
    ('45.0', '55.0')

    >>> is_out_of_range(duplicate)
    (True, True)


Duplicate of an analysis with result options
--------------------------------------------

Let's add some results options to service `Fe`:

    >>> results_options = [
    ...     {"ResultValue": "1", "ResultText": "Number 1"},
    ...     {"ResultValue": "2", "ResultText": "Number 2"},
    ...     {"ResultValue": "3", "ResultText": "Number 3"}]
    >>> Fe.setResultOptions(results_options)
    >>> Fe.getResultOptions()
    [{'ResultValue': '1', 'ResultText': 'Number 1'}, {'ResultValue': '2', 'ResultText': 'Number 2'}, {'ResultValue': '3', 'ResultText': 'Number 3'}]

Create a Sample and receive:

    >>> sample = new_sample([Fe])

Create a worksheet and assign the analyses:

    >>> analyses = sample.getAnalyses(full_objects=True)
    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> worksheet.addAnalyses(analyses)

Add a duplicate for analysis `Fe`:

    >>> worksheet.addDuplicateAnalyses(1)
    [<DuplicateAnalysis at /plone/worksheets/WS-002/...

    >>> duplicate = worksheet.getDuplicateAnalyses()[0]
    >>> fe = duplicate.getAnalysis()
    >>> fe
    <Analysis at /plone/clients/client-1/W-0003/Fe>

    >>> duplicate.getResultsRange()
    {}

Set a result for original analysis:

    >>> fe.setResult(2)
    >>> fe.getResult()
    '2'
    >>> fe.getFormattedResult()
    'Number 2'

The result range for duplicate does not longer consider duplicate variation,
rather expects an exact result:

    >>> duplicate.getResultsRange()
    {}

    >>> duplicate.setResult(1)
    >>> duplicate.getResult()
    '1'
    >>> duplicate.getFormattedResult()
    'Number 1'
    >>> duplicate.getResultsRange()
    {}
    >>> is_out_of_range(duplicate)
    (True, True)

    >>> duplicate.setResult(2)
    >>> duplicate.getResultsRange()
    {}
    >>> is_out_of_range(duplicate)
    (False, False)

    >>> duplicate.setResult(3)
    >>> duplicate.getResultsRange()
    {}
    >>> is_out_of_range(duplicate)
    (True, True)


Duplicate of an analysis with string results enabled
----------------------------------------------------

Let's add make the analysis `Au` to accept string results:

    >>> Au.setStringResult(True)

Create a Sample and receive:

    >>> sample = new_sample([Au])

Create a worksheet and assign the analyses:

    >>> analyses = sample.getAnalyses(full_objects=True)
    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> worksheet.addAnalyses(analyses)

Add a duplicate for analysis `Au`:

    >>> worksheet.addDuplicateAnalyses(1)
    [<DuplicateAnalysis at /plone/worksheets/WS-003/...

    >>> duplicate = worksheet.getDuplicateAnalyses()[0]
    >>> au = duplicate.getAnalysis()
    >>> au
    <Analysis at /plone/clients/client-1/W-0004/Au>

    >>> duplicate.getStringResult()
    True

    >>> duplicate.getResultsRange()
    {}

Submit a string result for original analysis:

    >>> au.setResult("Positive")
    >>> au.getResult()
    'Positive'

    >>> au.getFormattedResult()
    'Positive'

The result range for duplicate does not longer consider duplicate variation,
rather expects an exact result:

    >>> duplicate.getResultsRange()
    {}

    >>> duplicate.setResult("Negative")
    >>> duplicate.getResult()
    'Negative'
    >>> duplicate.getFormattedResult()
    'Negative'
    >>> duplicate.getResultsRange()
    {}
    >>> is_out_of_range(duplicate)
    (True, True)

    >>> duplicate.setResult("Positive")
    >>> duplicate.getResultsRange()
    {}
    >>> is_out_of_range(duplicate)
    (False, False)

But when we submit a numeric result for an analysis with string result enabled,
the system will behave as if it was indeed, a numeric result:

    >>> Au.setDuplicateVariation("10")
    >>> Au.getDuplicateVariation()
    '10.00'

    >>> Au.getStringResult()
    True

    >>> sample = new_sample([Au])
    >>> au = sample.getAnalyses(full_objects=True)[0]
    >>> worksheet.addAnalyses([au])

We add a duplicate for new analysis, that is located at slot number 3:

    >>> worksheet.addDuplicateAnalyses(src_slot=3)
    [<DuplicateAnalysis at /plone/worksheets/WS-003/...

    >>> duplicate = worksheet.getDuplicateAnalyses()
    >>> duplicate = filter(lambda dup: dup.getAnalysis() == au, duplicate)[0]
    >>> duplicate.getAnalysis()
    <Analysis at /plone/clients/client-1/W-0005/Au>

    >>> duplicate.getStringResult()
    True

    >>> duplicate.getResultsRange()
    {}

And we set a numeric result:

    >>> au.setResult(50)
    >>> results_range = duplicate.getResultsRange()
    >>> (results_range.min, results_range.max)
    ('45.0', '55.0')
