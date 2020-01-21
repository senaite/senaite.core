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
    >>> from zope.interface import alsoProvides
    >>> from zope.interface import noLongerProvides

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
    ...     return field.get(obj, uid=api.get_uid(service))

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

Create an Analysis Specification for `Water`:

    >>> sampletype_uid = api.get_uid(sampletype)
    >>> rr1 = {"uid": api.get_uid(Au), "min": 10, "max": 20, "warn_min": 5, "warn_max": 25}
    >>> rr2 = {"uid": api.get_uid(Cu), "min": 20, "max": 30, "warn_min": 15, "warn_max": 35}
    >>> rr3 = {"uid": api.get_uid(Fe), "min": 30, "max": 40, "warn_min": 25, "warn_max": 45}
    >>> rr4 = {"uid": api.get_uid(Mg), "min": 40, "max": 50, "warn_min": 35, "warn_max": 55}
    >>> rr = [rr1, rr2, rr3, rr4]
    >>> specification = api.create(setup.bika_analysisspecs, "AnalysisSpec", title="Lab Water Spec", SampleType=sampletype_uid, ResultsRange=rr)


Creation of a Sample with Specification
---------------------------------------

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

We need to re-apply the Specification for the Sample's results range to update:

    >>> sample.setSpecification(specification)
    >>> specification.getResultsRange() == sample.getResultsRange()
    True

As well as the analyses the sample contains:

    >>> au.getResultsRange() == get_results_range_from(specification, Au)
    True

    >>> rr_sample_au = au.getResultsRange()
    >>> (rr_sample_au.min, rr_sample_au.max)
    (15, 25)
