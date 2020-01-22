Infinite recursion when fetching dependencies from Service
==========================================================

This test checks that no infinite recursion error arises when fetching the
dependencies of a Service (via Calculation) that itself contains a keyword in
a calculation from another service bound to a calculation that refers to the
first one as well.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t ServicesCalculationRecursion.rst

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


Creation of Service with a Calculation that refers to itself
------------------------------------------------------------

The most common case is when the Calculation is assigned to the same Analysis
that is referred in the Calculation's formula:

    >>> Ca = api.create(setup.bika_analysisservices, "AnalysisService", title="Calcium", Keyword="Ca", Price="20", Category=category.UID())
    >>> Mg = api.create(setup.bika_analysisservices, "AnalysisService", title="Magnesium", Keyword="Mg", Price="20", Category=category.UID())

    >>> calc = api.create(setup.bika_calculations, "Calculation", title="Total Hardness")
    >>> calc.setFormula("[Ca] + [Mg]")
    >>> calc.getFormula()
    '[Ca] + [Mg]'

    >>> Ca.setCalculation(calc)
    >>> Ca.getCalculation()
    <Calculation at /plone/bika_setup/bika_calculations/calculation-1>

    >>> deps = Ca.getServiceDependencies()
    >>> sorted(map(lambda d: d.getKeyword(), deps))
    ['Ca', 'Mg']

    >>> deps = calc.getCalculationDependencies()
    >>> len(deps.keys())
    2

    >>> deps = calc.getCalculationDependencies(flat=True)
    >>> sorted(map(lambda d: d.getKeyword(), deps))
    ['Ca', 'Mg']

The other case is when the initial Service is referred indirectly, through a
calculation a dependency is bound to:

    >>> calc_mg = api.create(setup.bika_calculations, "Calculation", title="Test")
    >>> calc_mg.setFormula("[Ca] + [Ca]")
    >>> calc_mg.getFormula()
    '[Ca] + [Ca]'

    >>> Mg.setCalculation(calc_mg)
    >>> Mg.getCalculation()
    <Calculation at /plone/bika_setup/bika_calculations/calculation-2>

    >>> deps = Mg.getServiceDependencies()
    >>> sorted(map(lambda d: d.getKeyword(), deps))
    ['Ca', 'Mg']

    >>> deps = calc_mg.getCalculationDependencies()
    >>> len(deps.keys())
    2

    >>> deps = calc_mg.getCalculationDependencies(flat=True)
    >>> sorted(map(lambda d: d.getKeyword(), deps))
    ['Ca', 'Mg']

    >>> deps = Ca.getServiceDependencies()
    >>> sorted(map(lambda d: d.getKeyword(), deps))
    ['Ca', 'Mg']

    >>> deps = calc.getCalculationDependencies()
    >>> len(deps.keys())
    2

    >>> deps = calc.getCalculationDependencies(flat=True)
    >>> sorted(map(lambda d: d.getKeyword(), deps))
    ['Ca', 'Mg']