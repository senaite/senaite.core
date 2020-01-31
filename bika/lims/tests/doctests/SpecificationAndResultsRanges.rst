Specification and Results Ranges with Samples and analyses
==========================================================

Specification is an object containing a list of results ranges, each one refers
to the min/max/min_warn/max_warn values to apply for a given analysis service.
User can assign a Specification to a Sample, so the results of it's Analyses
will be checked against the results ranges provided by the Specification.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t SpecificationAndResultsRanges.rst

Test Setup
----------

Needed imports:

    >>> import transaction
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.analysisrequest import create_partition
    >>> from bika.lims.workflow import doActionFor as do_action_for

Functional Helpers:

    >>> def new_sample(services, specification=None, results_ranges=None):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': DateTime().strftime("%Y-%m-%d"),
    ...         'SampleType': sampletype.UID(),
    ...         'Analyses': map(api.get_uid, services),
    ...         'Specification': specification or None }
    ...
    ...     ar = create_analysisrequest(client, request, values, results_ranges=results_ranges)
    ...     transitioned = do_action_for(ar, "receive")
    ...     return ar

    >>> def get_analysis_from(sample, service):
    ...     service_uid = api.get_uid(service)
    ...     for analysis in sample.getAnalyses(full_objects=True):
    ...         if analysis.getServiceUID() == service_uid:
    ...             return analysis
    ...     return None

    >>> def get_results_range_from(obj, service):
    ...     field = obj.getField("ResultsRange")
    ...     return field.get(obj, search_by=api.get_uid(service))

    >>> def set_results_range_for(obj, results_range):
    ...     rrs = obj.getResultsRange()
    ...     uid = results_range["uid"]
    ...     rrs = filter(lambda rr: rr["uid"] != uid, rrs)
    ...     rrs.append(results_range)
    ...     obj.setResultsRange(rrs)


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
    >>> Au = api.create(setup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())
    >>> Cu = api.create(setup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID())
    >>> Fe = api.create(setup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Mg = api.create(setup.bika_analysisservices, "AnalysisService", title="Magnesium", Keyword="Mg", Price="20", Category=category.UID())
    >>> Zn = api.create(setup.bika_analysisservices, "AnalysisService", title="Zinc", Keyword="Zn", Price="10", Category=category.UID())

Create an Analysis Specification for `Water`:

    >>> sampletype_uid = api.get_uid(sampletype)
    >>> rr1 = {"uid": api.get_uid(Au), "min": 10, "max": 20, "warn_min": 5, "warn_max": 25}
    >>> rr2 = {"uid": api.get_uid(Cu), "min": 20, "max": 30, "warn_min": 15, "warn_max": 35}
    >>> rr3 = {"uid": api.get_uid(Fe), "min": 30, "max": 40, "warn_min": 25, "warn_max": 45}
    >>> rr4 = {"uid": api.get_uid(Mg), "min": 40, "max": 50, "warn_min": 35, "warn_max": 55}
    >>> rr5 = {"uid": api.get_uid(Zn), "min": 50, "max": 60, "warn_min": 45, "warn_max": 65}
    >>> rr = [rr1, rr2, rr3, rr4, rr5]
    >>> specification = api.create(setup.bika_analysisspecs, "AnalysisSpec", title="Lab Water Spec", SampleType=sampletype_uid, ResultsRange=rr)


Creation of a Sample with Specification
---------------------------------------

A given Specification can be assigned to the Sample during the creation process.
The results ranges of the mentioned Specification will be stored in ResultsRange
field from the Sample and the analyses will acquire those results ranges
individually.

Specification from Sample is history-aware, so even if the Specification object
is changed after its assignment to the Sample, the Results Ranges from either
the Sample and its Analyses will remain untouched.

Create a Sample and receive:

    >>> services = [Au, Cu, Fe, Mg]
    >>> sample = new_sample(services, specification=specification)

The sample has the specification assigned:

    >>> sample.getSpecification()
    <AnalysisSpec at /plone/bika_setup/bika_analysisspecs/analysisspec-1>

And its results ranges match with the sample's `ResultsRange` field value:

    >>> specification.getResultsRange() == sample.getResultsRange()
    True

And the analyses the sample contains have the results ranges properly set:

    >>> au = get_analysis_from(sample, Au)
    >>> au.getResultsRange() == get_results_range_from(specification, Au)
    True

    >>> cu = get_analysis_from(sample, Cu)
    >>> cu.getResultsRange() == get_results_range_from(specification, Cu)
    True

    >>> fe = get_analysis_from(sample, Fe)
    >>> fe.getResultsRange() == get_results_range_from(specification, Fe)
    True

    >>> mg = get_analysis_from(sample, Mg)
    >>> mg.getResultsRange() == get_results_range_from(specification, Mg)
    True

We can change a result range by using properties:

    >>> rr_au = au.getResultsRange()
    >>> rr_au.min = 11
    >>> rr_au.max = 21
    >>> (rr_au.min, rr_au.max)
    (11, 21)

Or using it as a dict:

    >>> rr_au["min"] = 15
    >>> rr_au["max"] = 25
    >>> (rr_au["min"], rr_au["max"])
    (15, 25)

If we change this results range in the Specification object, this won't take any
effect to neither the Sample nor analyses:

    >>> set_results_range_for(specification, rr_au)
    >>> specification.getResultsRange() == sample.getResultsRange()
    False

    >>> au.getResultsRange() == get_results_range_from(specification, Au)
    False

    >>> get_results_range_from(sample, Au) == au.getResultsRange()
    True

    >>> rr_sample_au = au.getResultsRange()
    >>> (rr_sample_au.min, rr_sample_au.max)
    (10, 20)

If we re-apply the Specification, nothing will change though, because its `uid`
is still the same:

    >>> sample.setSpecification(specification)
    >>> specification.getResultsRange() == sample.getResultsRange()
    False

But the ResultsRange value from Sample is updated accordingly if we set the
specification to `None` first:

    >>> sample.setSpecification(None)
    >>> sample.setSpecification(specification)
    >>> specification.getResultsRange() == sample.getResultsRange()
    True

As well as the analyses the sample contains:

    >>> au.getResultsRange() == get_results_range_from(specification, Au)
    True

    >>> rr_sample_au = au.getResultsRange()
    >>> (rr_sample_au.min, rr_sample_au.max)
    (15, 25)

Removal of Analyses from a Sample with Specifications
-----------------------------------------------------

User can remove analyses from the Sample. If the user removes one of the
analyses, the Specification assigned to the Sample will remain intact, as well
as Sample's Results Range:

    >>> sample.setAnalyses([Au, Cu, Fe])
    >>> analyses = sample.objectValues()
    >>> sorted(analyses, key=lambda an: an.getKeyword())
    [<Analysis at /plone/clients/client-1/W-0001/Au>, <Analysis at /plone/clients/client-1/W-0001/Cu>, <Analysis at /plone/clients/client-1/W-0001/Fe>]

    >>> sample.getSpecification()
    <AnalysisSpec at /plone/bika_setup/bika_analysisspecs/analysisspec-1>

    >>> specification.getResultsRange() == sample.getResultsRange()
    True


Addition of Analyses to a Sample with Specifications
----------------------------------------------------

User can add new analyses to the Sample as well. If the Sample has an
Specification set and the specification had a results range registered for
such analysis, the result range for the new analysis will be set automatically:

    >>> sample.setAnalyses([Au, Cu, Fe, Zn])
    >>> sample.getSpecification()
    <AnalysisSpec at /plone/bika_setup/bika_analysisspecs/analysisspec-1>

    >>> zn = get_analysis_from(sample, Zn)
    >>> zn.getResultsRange() == get_results_range_from(specification, Zn)
    True

If we reset an Analysis with it's own ResultsRange, different from the range
defined by the Specification, the system does not clear the Specification:

    >>> rr_zn = zn.getResultsRange()
    >>> rr_zn.min = 55
    >>> sample.setAnalyses([Au, Cu, Fe, Zn], specs=[rr_zn])
    >>> sample.getSpecification()
    <AnalysisSpec at /plone/bika_setup/bika_analysisspecs/analysisspec-1>

and Sample's ResultsRange is kept unchanged:

    >>> sample_rr = sample.getResultsRange()
    >>> len(sample_rr)
    5

with result range for `Zn` unchanged:

    >>> sample_rr_zn = sample.getResultsRange(search_by=api.get_uid(Zn))
    >>> sample_rr_zn.min
    50

But analysis' result range has indeed changed:

    >>> zn.getResultsRange().min
    55

If we re-apply the Specification, the result range for `Zn`, as well as for the
Sample, are reestablished:

    >>> sample.setSpecification(None)
    >>> sample.setSpecification(specification)
    >>> specification.getResultsRange() == sample.getResultsRange()
    True

    >>> zn.getResultsRange() == get_results_range_from(specification, Zn)
    True

    >>> zn.getResultsRange().min
    50


Sample with Specifications and Partitions
-----------------------------------------

When a sample has partitions, the Specification set to the root Sample is
populated to all its descendants:

    >>> partition = create_partition(sample, request, [zn])
    >>> partition
    <AnalysisRequest at /plone/clients/client-1/W-0001-P01>

    >>> zn = get_analysis_from(partition, Zn)
    >>> zn
    <Analysis at /plone/clients/client-1/W-0001-P01/Zn>

The partition keeps the Specification and ResultsRange by its own:

    >>> partition.getSpecification()
    <AnalysisSpec at /plone/bika_setup/bika_analysisspecs/analysisspec-1>

    >>> partition.getResultsRange() == specification.getResultsRange()
    True

If we reset an Analysis with it's own ResultsRange, different from the range
defined by the Specification, the system does not clear the Specification,
neither from the root sample nor the partition:

    >>> rr_zn = zn.getResultsRange()
    >>> rr_zn.min = 56
    >>> partition.setAnalyses([Zn], specs=[rr_zn])

    >>> sample.getSpecification()
    <AnalysisSpec at /plone/bika_setup/bika_analysisspecs/analysisspec-1>

    >>> partition.getSpecification()
    <AnalysisSpec at /plone/bika_setup/bika_analysisspecs/analysisspec-1>

And Results Range from both Sample and partition are kept untouched:

    >>> sample.getSpecification()
    <AnalysisSpec at /plone/bika_setup/bika_analysisspecs/analysisspec-1>

    >>> sample.getResultsRange() == specification.getResultsRange()
    True

    >>> partition.getSpecification()
    <AnalysisSpec at /plone/bika_setup/bika_analysisspecs/analysisspec-1>

    >>> partition.getResultsRange() == specification.getResultsRange()
    True
