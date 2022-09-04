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


Multi-component analyses
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
