Reference Sample from a Reference Definition
--------------------------------------------

A reference definition holds the expected values of a control or a blank,
and a reference sample points at the definition it was bought against. The
sample may state values of its own, and then those count; otherwise it takes
the definition's.

This matters because the expected values are what decides which services a
reference sample supports. A sample that links a definition and holds no
values of its own supports nothing, and is offered on a worksheet as a
control that adds no analysis.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t ReferenceSampleFromDefinition


Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from DateTime import DateTime
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles

Variables:

    >>> portal = self.portal
    >>> setup = portal.setup
    >>> bikasetup = portal.bika_setup

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager", "Analyst"])
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> supplier = api.create(setup.suppliers, "Supplier", Name="Naralabs")

Two analysis services:

    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Category=category.UID())
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Category=category.UID())

A definition that expects one milligram of copper, give or take a tenth:

    >>> results = [{"uid": api.get_uid(Cu), "result": "1",
    ...             "min": "0.9", "max": "1.1", "error": "0"}]
    >>> definition = api.create(bikasetup.bika_referencedefinitions,
    ...                         "ReferenceDefinition",
    ...                         title="Copper control",
    ...                         ReferenceResults=results)


A sample takes the values of its definition
...........................................

A sample created with nothing but the definition reports the definition's
values as its own:

    >>> sample = api.create(supplier, "ReferenceSample", title="Lot A",
    ...                     ReferenceDefinition=api.get_uid(definition),
    ...                     ExpiryDate=date_future)

    >>> [(r["uid"] == api.get_uid(Cu), r["result"], r["min"], r["max"])
    ...  for r in sample.getReferenceResults()]
    [(True, '1', '0.9', '1.1')]

And therefore supports the service the definition names, which is what a
worksheet asks before it offers the sample as a control:

    >>> api.get_uid(Cu) in sample.getSupportedServices()
    True

    >>> sorted(sample.getResultsRangeDict().keys()) == [api.get_uid(Cu)]
    True


Its own values win
..................

A sample that states values of its own is not overruled by its definition:

    >>> own = [{"uid": api.get_uid(Fe), "result": "5",
    ...         "min": "4", "max": "6", "error": "0"}]
    >>> sample.setReferenceResults(own)

    >>> [(r["uid"] == api.get_uid(Fe), r["result"]) for r in sample.getReferenceResults()]
    [(True, '5')]

    >>> api.get_uid(Cu) in sample.getSupportedServices()
    False

Clearing them hands the sample back to its definition:

    >>> sample.setReferenceResults([])
    >>> api.get_uid(Cu) in sample.getSupportedServices()
    True


Without a definition there is nothing to inherit
................................................

A sample that points at no definition and holds no values of its own
supports nothing, and says so rather than failing:

    >>> orphan = api.create(supplier, "ReferenceSample", title="Lot B",
    ...                     ExpiryDate=date_future)
    >>> orphan.getReferenceResults()
    []
    >>> orphan.getSupportedServices()
    []
