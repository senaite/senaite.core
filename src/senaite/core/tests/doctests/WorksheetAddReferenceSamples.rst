Worksheet Add Reference Samples
-------------------------------

Reference samples are added to a worksheet through the `add_control` and
`add_blank` views. Both listings offer every valid reference sample,
regardless of whether it supports one of the services assigned to the
worksheet. The services the worksheet does run are preselected.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t WorksheetAddReferenceSamples


Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor
    >>> from DateTime import DateTime
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = portal.bika_setup

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager", "Analyst"])
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> supplier = api.create(setup.suppliers, "Supplier", Name="Naralabs")

Two analysis services, of which only one ends up in the worksheet:

    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Category=category.UID())
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Category=category.UID())

A control and a blank for each of them:

    >>> def new_reference(title, service, blank):
    ...     results = [{"uid": api.get_uid(service), "result": "1",
    ...                 "min": "0.9", "max": "1.1"}]
    ...     return api.create(supplier, "ReferenceSample", title=title,
    ...                       Blank=blank, ExpiryDate=date_future,
    ...                       ReferenceResults=results)

    >>> control_cu = new_reference("Control Cu", Cu, False)
    >>> control_fe = new_reference("Control Fe", Fe, False)
    >>> blank_cu = new_reference("Blank Cu", Cu, True)
    >>> blank_fe = new_reference("Blank Fe", Fe, True)

And a worksheet that holds a single copper analysis:

    >>> values = {
    ...     "Client": api.get_uid(client),
    ...     "Contact": api.get_uid(contact),
    ...     "DateSampled": date_now,
    ...     "SampleType": api.get_uid(sampletype),
    ... }
    >>> sample = create_analysisrequest(client, request, values, [api.get_uid(Cu)])
    >>> success = doActionFor(sample, "receive")
    >>> worksheet = api.create(portal.worksheets, "Worksheet", Analyst="test_user_1_")
    >>> analysis = api.get_object(sample.getAnalyses()[0])
    >>> worksheet.addAnalysis(analysis)

Functional helpers to read a listing:

    >>> def get_listed(view_name, worksheet=worksheet):
    ...     view = api.get_view(view_name, context=worksheet, request=request)
    ...     return sorted([api.get_title(b) for b in view.search()])

    >>> def get_preselected(view_name, sample):
    ...     view = api.get_view(view_name, context=worksheet, request=request)
    ...     choices = view.make_supported_services_choices(sample)
    ...     return sorted([c["ResultText"] for c in choices if c["selected"]])


Controls
........

Every valid control is listed, including the one for a service this
worksheet does not run:

    >>> get_listed("add_control")
    ['Control Cu', 'Control Fe']

Blanks are never listed among the controls:

    >>> "Blank Cu" in get_listed("add_control")
    False


Blanks
......

The same applies to blanks:

    >>> get_listed("add_blank")
    ['Blank Cu', 'Blank Fe']

And controls are never listed among the blanks:

    >>> "Control Cu" in get_listed("add_blank")
    False


Preselection
............

The worksheet runs copper, so copper is preselected:

    >>> get_preselected("add_control", control_cu)
    ['Copper']

A sample for a service the worksheet does not run comes with nothing
preselected. It is offered, but the choice is left to the user:

    >>> get_preselected("add_control", control_fe)
    []


Invalid samples stay out
........................

Dropping the filter by service does not make expired samples available.
Only the check that never made sense is gone, not the ones that protect
the results:

    >>> date_past = (DateTime() - 5).strftime("%Y-%m-%d")
    >>> expired = new_reference("Control Expired", Fe, False)
    >>> expired.setExpiryDate(date_past)
    >>> expired.reindexObject()
    >>> "Control Expired" in get_listed("add_control")
    False


Adding a sample the worksheet has no service for
................................................

A control for a service the worksheet does not run can be added, and it
brings its own service along:

    >>> added = worksheet.addReferenceAnalyses(control_fe, [api.get_uid(Fe)])
    >>> len(added)
    1

    >>> added[0].getKeyword()
    'Fe'

    >>> api.get_workflow_status_of(added[0])
    'assigned'

Reference assigned before the routine analyses
..............................................

A reference sample can be assigned to a worksheet that is still empty. The
customer sample does not store a reference to its quality control, the link
is resolved through the shared worksheet at query time, so the order in
which references and routine analyses are assigned does not matter.

An empty worksheet, with the control assigned first:

    >>> ws2 = api.create(portal.worksheets, "Worksheet", Analyst="test_user_1_")
    >>> ws2.getAnalyses()
    []

    >>> added = ws2.addReferenceAnalyses(control_cu, [api.get_uid(Cu)])
    >>> len(added)
    1

A new customer sample does not see it yet, because none of its analyses is
on that worksheet:

    >>> sample2 = create_analysisrequest(client, request, values, [api.get_uid(Cu)])
    >>> success = doActionFor(sample2, "receive")
    >>> sample2.getQCAnalyses()
    []

Assigning the routine analysis afterwards is enough:

    >>> analysis2 = api.get_object(sample2.getAnalyses()[0])
    >>> ws2.addAnalysis(analysis2)

    >>> qc = sample2.getQCAnalyses()
    >>> len(qc)
    1

    >>> qc[0].portal_type
    'ReferenceAnalysis'

    >>> qc[0].getKeyword()
    'Cu'

The reference analysis sits on the worksheet the sample was added to:

    >>> api.get_uid(qc[0].getWorksheet()) == api.get_uid(ws2)
    True


This also covers the empty worksheet. It has no services to match against,
which used to leave the listing empty and made assigning a reference first
impossible through the UI:

    >>> ws3 = api.create(portal.worksheets, "Worksheet", Analyst="test_user_1_")
    >>> ws3.getAnalyses()
    []

    >>> get_listed("add_control", ws3)
    ['Control Cu', 'Control Fe']
