Multiple component analysis
---------------------------

Multiple component analyses allow to measure multiple chemical analytes
simultaneously with a single analyzer, without using filters or moving parts.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t MultiComponentAnalysis


Test Setup
..........

Needed Imports:

    >>> from DateTime import DateTime
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles

Functional Helpers:

    >>> def new_sample(client, contact, sample_type, services):
    ...     values = {
    ...         'Client': api.get_uid(client),
    ...         'Contact': api.get_uid(contact),
    ...         'DateSampled': DateTime().strftime("%Y-%m-%d"),
    ...         'SampleType': api.get_uid(sample_type),
    ...     }
    ...     uids = map(api.get_uid, services)
    ...     sample = create_analysisrequest(client, request, values, uids)
    ...     return sample

    >>> def do_action(object, transition_id):
    ...      return do_action_for(object, transition_id)[0]

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_setup()

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sample_type = api.create(setup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> lab_contact = api.create(setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.bika_departments, "Department", title="Chemistry", Manager=lab_contact)
    >>> category = api.create(setup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> setup.setSelfVerificationEnabled(True)


Multi-component Service
.......................

Create the multi-component service, that is made of analytes:

    >>> analytes = [
    ...     {"keyword": "Pb", "title": "Lead"},
    ...     {"keyword": "Hg", "title": "Mercury"},
    ...     {"keyword": "As", "title": "Arsenic"},
    ...     {"keyword": "Cd", "title": "Cadmium"},
    ...     {"keyword": "Cu", "title": "Copper"},
    ...     {"keyword": "Ni", "title": "Nickel"},
    ...     {"keyword": "Zn", "title": "Zinc"},
    ... ]
    >>> metals = api.create(setup.bika_analysisservices, "AnalysisService",
    ...                     title="ICP Metals", Keyword="Metals", Price="15",
    ...                     Analytes=analytes, Category=category.UID())
    >>> metals.isMultiComponent()
    True


Multi-component analysis
........................

Although there is only one "Multi-component" service, the system creates
the analytes (from type "Analysis") automatically when the service is assigned
to a Sample:

    >>> sample = new_sample(client, contact, sample_type, [metals])
    >>> analyses = sample.getAnalyses(full_objects=True)
    >>> len(analyses)
    8

The multi-component is always first and followed by the Analytes, with same
order as defined in the Service:

    >>> [an.getKeyword() for an in analyses]
    ['Metals', 'Pb', 'Hg', 'As', 'Cd', 'Cu', 'Ni', 'Zn']

From a multi-component analysis:

    >>> multi_component = analyses[0]
    >>> multi_component.isMultiComponent()
    True

    >>> multi_component.isAnalyte()
    False

one can extract its analytes as well:

    >>> analytes = multi_component.getAnalytes()
    >>> [an.getKeyword() for an in analytes]
    ['Pb', 'Hg', 'As', 'Cd', 'Cu', 'Ni', 'Zn']

    >>> analytes_uids = [an.UID() for an in analytes]
    >>> analytes_uids == multi_component.getRawAnalytes()
    True

From an analyte, one can get the multi-component analysis that belongs to:

    >>> pb = analytes[0]
    >>> pb.isAnalyte()
    True
    >>> pb.isMultiComponent()
    False
    >>> multi_component == pb.getMultiComponentAnalysis()
    True
    >>> multi_component.UID() == pb.getRawMultiComponentAnalysis()
    True


Submission of results
.....................

Receive the sample:

    >>> do_action(sample, "receive")
    True

Is not possible to set a result to a multi-component directly:

    >>> multi_component.setResult("Something")
    Traceback (most recent call last):
    [...]
    ValueError: setResult is not supported for Multi-component analyses

But a "NA" (*No apply*) result is set automatically as soon as a result for
any of its analytes is set:

    >>> multi_component.getResult()
    ''

    >>> pb.setResult(12)
    >>> multi_component.getResult()
    'NA'

Is not possible to manually submit a multi-component analysis, is automatically
submitted when results for all analytes are captured and submitted:

    >>> isTransitionAllowed(multi_component, "submit")
    False

    >>> isTransitionAllowed(pb, "submit")
    True

    >>> api.get_review_status(multi_component)
    'unassigned'

    >>> results = [an.setResult(12) for an in analytes]
    >>> submitted = [do_action(an, "submit") for an in analytes]
    >>> all(submitted)
    True

    >>> api.get_review_status(multi_component)
    'to_be_verified'


Retraction of results
.....................

Create the sample, receive and capture results:

    >>> sample = new_sample(client, contact, sample_type, [metals])
    >>> success = do_action(sample, "receive")
    >>> analyses = sample.getAnalyses(full_objects=True)
    >>> multi_component = filter(lambda an: an.isMultiComponent(), analyses)[0]
    >>> analytes = multi_component.getAnalytes()
    >>> results = [an.setResult(12) for an in analytes]
    >>> submitted = [do_action(an, "submit") for an in analytes]
    >>> all(submitted)
    True

Analytes cannot be retracted, but the multi-component analysis only. The reason
is that the retraction involves the creation of a retest. The detection of the
concentrations of analytes in a multicomponent analysis takes place in a single
analytical procedure, usually by an spectrometer. Thus, it does not make sense
to create a retest for a single analyte - if there is an inconsistency, the
whole multi-component analysis has to be run again:

    >>> analyte = analytes[0]
    >>> isTransitionAllowed(analyte, "retract")
    False

    >>> isTransitionAllowed(multi_component, "retract")
    True

When a multiple component analysis is retracted, a new multi-component test
is added, with new analytes. Existing analytes and multi-component are all
transitioned to "retracted" status:

    >>> do_action(multi_component, "retract")
    True

    >>> api.get_review_status(multi_component)
    'retracted'

    >>> list(set([api.get_review_status(an) for an in analytes]))
    ['retracted']

    >>> retest = multi_component.getRetest()
    >>> retest.isMultiComponent()
    True

    >>> api.get_review_status(retest)
    'unassigned'

    >>> retest_analytes = retest.getAnalytes()
    >>> list(set([api.get_review_status(an) for an in retest_analytes]))
    ['unassigned']


Rejection of results
....................

Create the sample, receive and capture results:

    >>> sample = new_sample(client, contact, sample_type, [metals])
    >>> success = do_action(sample, "receive")
    >>> analyses = sample.getAnalyses(full_objects=True)
    >>> multi_component = filter(lambda an: an.isMultiComponent(), analyses)[0]
    >>> analytes = multi_component.getAnalytes()
    >>> results = [an.setResult(12) for an in analytes]
    >>> submitted = [do_action(an, "submit") for an in analytes]
    >>> all(submitted)
    True

Both individual analytes or the whole multi-component analysis can be rejected.
Reason is that although a multi-component analysis takes place in a single
run/analytical procedure, one might want to "discard" results for some of the
analytes/components after the analysis has run without compromising the validity
of the analytical process:

    >>> analyte = analytes[0]
    >>> isTransitionAllowed(analyte, "reject")
    True

    >>> isTransitionAllowed(multi_component, "reject")
    True

If I reject an analyte, the multi_component analysis is not affected:

    >>> do_action(analyte, "reject")
    True

    >>> api.get_review_status(analyte)
    'rejected'

    >>> api.get_review_status(multi_component)
    'to_be_verified'

However, if I reject the multiple component analyses, all analytes are rejected
automatically:

    >>> statuses = list(set([api.get_review_status(an) for an in analytes]))
    >>> sorted(statuses)
    ['rejected', 'to_be_verified']

    >>> do_action(multi_component, "reject")
    True

    >>> api.get_review_status(multi_component)
    'rejected'

    >>> list(set([api.get_review_status(an) for an in analytes]))
    ['rejected']


Retest of multi-component analysis
..................................

Create the sample, receive and capture results:

    >>> sample = new_sample(client, contact, sample_type, [metals])
    >>> success = do_action(sample, "receive")
    >>> analyses = sample.getAnalyses(full_objects=True)
    >>> multi_component = filter(lambda an: an.isMultiComponent(), analyses)[0]
    >>> analytes = multi_component.getAnalytes()
    >>> results = [an.setResult(12) for an in analytes]
    >>> submitted = [do_action(an, "submit") for an in analytes]
    >>> all(submitted)
    True

Analytes cannot be retested, but the multi-component analysis only. The
detection of the concentrations of analytes in a multi-component analysis takes
place in a single analytical procedure. Therefore, it does not make sense to
retest analytes individually, but the whole multi-component analysis:

    >>> analyte = analytes[0]
    >>> isTransitionAllowed(analyte, "retest")
    False

    >>> isTransitionAllowed(multi_component, "retest")
    True

When a multiple component analysis is retested, a new multi-component test
is added, with new analytes. Existing analytes and multi-component are all
transitioned to "verified" status:

    >>> do_action(multi_component, "retest")
    True

    >>> api.get_review_status(multi_component)
    'verified'

    >>> list(set([api.get_review_status(an) for an in analytes]))
    ['verified']

    >>> retest = multi_component.getRetest()
    >>> retest.isMultiComponent()
    True

    >>> api.get_review_status(retest)
    'unassigned'

    >>> retest_analytes = retest.getAnalytes()
    >>> list(set([api.get_review_status(an) for an in retest_analytes]))
    ['unassigned']


Verification of multi-component analysis
........................................

Create the sample, receive and capture results:

    >>> sample = new_sample(client, contact, sample_type, [metals])
    >>> success = do_action(sample, "receive")
    >>> analyses = sample.getAnalyses(full_objects=True)
    >>> multi_component = filter(lambda an: an.isMultiComponent(), analyses)[0]
    >>> analytes = multi_component.getAnalytes()
    >>> results = [an.setResult(12) for an in analytes]
    >>> submitted = [do_action(an, "submit") for an in analytes]
    >>> all(submitted)
    True

Analytes cannot be verified, but the multi-component analysis only. The
detection of the concentrations of analytes in a multi-component analysis takes
place in a single analytical procedure. Therefore, it does not make sense to
verify analytes individually, but the whole multi-component analysis:

    >>> analyte = analytes[0]
    >>> isTransitionAllowed(analyte, "verify")
    False

    >>> isTransitionAllowed(multi_component, "verify")
    True

When a multiple component analysis is verified, all analytes are automatically
verified as well:

    >>> do_action(multi_component, "verify")
    True

    >>> api.get_review_status(multi_component)
    'verified'

    >>> list(set([api.get_review_status(an) for an in analytes]))
    ['verified']


Assignment of multi-component analysis
......................................

Create the sample and receive:

    >>> sample = new_sample(client, contact, sample_type, [metals])
    >>> success = do_action(sample, "receive")
    >>> analyses = sample.getAnalyses(full_objects=True)
    >>> multi_component = filter(lambda an: an.isMultiComponent(), analyses)[0]
    >>> analytes = multi_component.getAnalytes()

Status of multi-component and analytes is 'unassigned':

    >>> api.get_review_status(multi_component)
    'unassigned'

    >>> list(set([api.get_review_status(an) for an in analytes]))
    ['unassigned']

Create a worksheet:

    >>> worksheet = api.create(portal.worksheets, "Worksheet")

When a multi-component is assigned to a worksheet, the analytes are assigned
as well:

    >>> worksheet.addAnalyses([multi_component])
    >>> multi_component.getWorksheet() == worksheet
    True

    >>> assigned = [analyte.getWorksheet() == worksheet for analyte in analytes]
    >>> all(assigned)
    True

And all their statuses are now 'assigned':

    >>> api.get_review_status(multi_component)
    'assigned'

    >>> list(set([api.get_review_status(an) for an in analytes]))
    ['assigned']


Multi-component with default result
...................................

Set a default result for a Multi-component analysis:

    >>> metals.setDefaultResult("12")

Create a sample:

    >>> sample = new_sample(client, contact, sample_type, [metals])
    >>> analyses = sample.getAnalyses(full_objects=True)
    >>> multi_component = filter(lambda an: an.isMultiComponent(), analyses)[0]
    >>> analytes = multi_component.getAnalytes()

Analytes have the default result set, but the multi-component:

    >>> list(set([analyte.getResult() for analyte in analytes]))
    ['12']

    >>> multi_component.getResult()
    'NA'

The Result Capture Date is not set in any case:

    >>> filter(None, ([analyte.getResultCaptureDate() for an in analytes]))
    []

    >>> multi_component.getResultCaptureDate()

Restore the default result for a Multi-component analysis:

    >>> metals.setDefaultResult(None)


Invalidation of samples with multi-component analyses
.....................................................

Create the sample, receive and submit:

    >>> sample = new_sample(client, contact, sample_type, [metals])
    >>> success = do_action(sample, "receive")
    >>> analyses = sample.getAnalyses(full_objects=True)
    >>> multi = filter(lambda an: an.isMultiComponent(), analyses)[0]
    >>> analytes = multi.getAnalytes()
    >>> results = [an.setResult(12) for an in analytes]
    >>> submitted = [do_action(an, "submit") for an in analytes]

Verifying the multi-component analysis leads the sample to verified status too:

    >>> success = do_action(multi, "verify")
    >>> api.get_review_status(sample)
    'verified'

Invalidate the sample. The retest sample created automatically contains a copy
of the original multi-component analysis, with analytes properly assigned:

    >>> success = do_action(sample, "invalidate")
    >>> api.get_review_status(sample)
    'invalid'

    >>> retest = sample.getRetest()
    >>> retests = retest.getAnalyses(full_objects=True)
    >>> multi = filter(lambda an: an.isMultiComponent(), retests)[0]
    >>> multi.getRequest() == retest
    True

The analytes from the retest are all assigned to the new multi-component:

    >>> multi_analytes = sorted(multi.getAnalytes())
    >>> analytes = sorted(filter(lambda an: an.isAnalyte(), retests))
    >>> multi_analytes == analytes
    True

    >>> all([an.getMultiComponentAnalysis() == multi for an in analytes])
    True
