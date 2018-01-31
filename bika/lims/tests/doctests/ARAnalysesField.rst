AR Analyses Field
=================

This field manages Analyses for Analysis Requests.

It is capable to perform the following tasks:

  - Create Analyses from Analysis Services
  - Delete assigned Analyses
  - Update Prices of assigned Analyses
  - Update Specifications of assigned Analyses
  - Update Interim Fields of assigned Analyses

Running this test from the buildout directory::

    bin/test test_textual_doctests -t ARAnalysesField


Test Setup
----------

Imports:

    >>> import transaction
    >>> from operator import methodcaller
    >>> from DateTime import DateTime
    >>> from plone import api as ploneapi

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

Variables::

    >>> date_now = timestamp()
    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.bika_setup
    >>> calculations = setup.bika_calculations
    >>> sampletypes = setup.bika_sampletypes
    >>> samplepoints = setup.bika_samplepoints
    >>> analysiscategories = setup.bika_analysiscategories
    >>> analysisspecs = setup.bika_analysisspecs
    >>> analysisservices = setup.bika_analysisservices
    >>> labcontacts = setup.bika_labcontacts
    >>> worksheets = setup.worksheets
    >>> storagelocations = setup.bika_storagelocations
    >>> samplingdeviations = setup.bika_samplingdeviations
    >>> sampleconditions = setup.bika_sampleconditions
    >>> portal_url = portal.absolute_url()
    >>> setup_url = portal_url + "/bika_setup"

Test User:

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])


Prepare Test Environment
------------------------

Create Client:

    >>> clients = self.portal.clients
    >>> client = api.create(clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> client
    <Client at /plone/clients/client-1>

Create some Contact(s):

    >>> contact1 = api.create(client, "Contact", Firstname="Client", Surname="One")
    >>> contact1
    <Contact at /plone/clients/client-1/contact-1>

    >>> contact2 = api.create(client, "Contact", Firstname="Client", Surname="Two")
    >>> contact2
    <Contact at /plone/clients/client-1/contact-2>

Create a Sample Type:

    >>> sampletype = api.create(sampletypes, "SampleType", Prefix="water", MinimumVolume="100 ml")
    >>> sampletype
    <SampleType at /plone/bika_setup/bika_sampletypes/sampletype-1>

Create a Sample Point:

    >>> samplepoint = api.create(samplepoints, "SamplePoint", title="Lake Python")
    >>> samplepoint
    <SamplePoint at /plone/bika_setup/bika_samplepoints/samplepoint-1>

Create an Analysis Category:

    >>> analysiscategory = api.create(analysiscategories, "AnalysisCategory", title="Water")
    >>> analysiscategory
    <AnalysisCategory at /plone/bika_setup/bika_analysiscategories/analysiscategory-1>

Create Analysis Service for PH (Keyword: `PH`):

    >>> analysisservice1 = api.create(analysisservices, "AnalysisService", title="PH", ShortTitle="ph", Category=analysiscategory, Keyword="PH", Price="10")
    >>> analysisservice1
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-1>

Create Analysis Service for Magnesium (Keyword: `MG`):

    >>> analysisservice2 = api.create(analysisservices, "AnalysisService", title="Magnesium", ShortTitle="mg", Category=analysiscategory, Keyword="MG", Price="20")
    >>> analysisservice2
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-2>

Create Analysis Service for Calcium (Keyword: `CA`):

    >>> analysisservice3 = api.create(analysisservices, "AnalysisService", title="Calcium", ShortTitle="ca", Category=analysiscategory, Keyword="CA", Price="30")
    >>> analysisservice3
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-3>

Create Analysis Service for Total Hardness (Keyword: `THCaCO3`):

    >>> analysisservice4 = api.create(analysisservices, "AnalysisService", title="Total Hardness", ShortTitle="Tot. Hard", Category=analysiscategory, Keyword="THCaCO3", Price="40")
    >>> analysisservice4
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-4>

Create some Calculations with Formulas referencing existing AS keywords:

    >>> calc1 = api.create(calculations, "Calculation", title="Round")
    >>> calc1.setFormula("round(12345, 2)")

    >>> calc2 = api.create(calculations, "Calculation", title="A in ppt")
    >>> calc2.setFormula("[A] * 1000")

    >>> calc3 = api.create(calculations, "Calculation", title="B in ppt")
    >>> calc3.setFormula("[B] * 1000")

    >>> calc4 = api.create(calculations, "Calculation", title="Total Hardness")
    >>> calc4.setFormula("[CA] + [MG]")

Assign the calculations to the Analysis Services:

    >>> analysisservice1.setCalculation(calc1)
    >>> analysisservice2.setCalculation(calc2)
    >>> analysisservice3.setCalculation(calc3)
    >>> analysisservice4.setCalculation(calc4)

Create an Analysis Specification for `Water`:

    >>> sampletype_uid = api.get_uid(sampletype)

    >>> rr1 = {"keyword": "PH", "min": 5, "max": 7, "error": 10, "hidemin": "", "hidemax": "", "rangecomment": "Lab PH Spec"}
    >>> rr2 = {"keyword": "MG", "min": 5, "max": 7, "error": 10, "hidemin": "", "hidemax": "", "rangecomment": "Lab MG Spec"}
    >>> rr3 = {"keyword": "CA", "min": 5, "max": 7, "error": 10, "hidemin": "", "hidemax": "", "rangecomment": "Lab CA Spec"}
    >>> rr = [rr1, rr2, rr3]

    >>> analysisspec1 = api.create(analysisspecs, "AnalysisSpec", title="Lab Water Spec", SampleType=sampletype_uid, ResultsRange=rr)

Create an Analysis Request:

    >>> values = {
    ...     'Client': client.UID(),
    ...     'Contact': contact1.UID(),
    ...     'CContact': contact2.UID(),
    ...     'SamplingDate': date_now,
    ...     'DateSampled': date_now,
    ...     'SampleType': sampletype.UID(),
    ...     'Priority': '1',
    ... }

    >>> service_uids = [analysisservice1.UID()]
    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar
    <AnalysisRequest at /plone/clients/client-1/water-0001-R01>


ARAnalysesField
---------------

This field maintains `Analyses` within `AnalysesRequests`:

    >>> field = ar.getField("Analyses")
    >>> field.type
    'analyses'

    >>> from bika.lims.interfaces import IARAnalysesField
    >>> IARAnalysesField.providedBy(field)
    True


Getting Analyses
................

The `get` method returns a list of assined analyses brains:

    >>> field.get(ar)
    [<Products.ZCatalog.Catalog.mybrains object at ...>]

The full objects can be obtained by passing in `full_objects=True`:

    >>> field.get(ar, full_objects=True)
    [<Analysis at /plone/clients/client-1/water-0001-R01/PH>]

The analysis `PH` is now contained in the AR:

    >>> ar.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/water-0001-R01/PH>]


Setting Analyses
................

The `set` method returns a list of new created analyses.

The field takes the following parameters:

    - items is a list that contains the items to be set:
        The list can contain Analysis objects/brains, AnalysisService
        objects/brains and/or Analysis Service uids.

    - prices is a dictionary:
        key = AnalysisService UID
        value = price

    - specs is a list of dictionaries:
        key = AnalysisService UID
        value = dictionary: defined in ResultsRange field definition

Pass in all prior created Analysis Services:

    >>> all_services = [analysisservice1, analysisservice2, analysisservice3]
    >>> new_analyses = field.set(ar, all_services)

We expect to have now the `CA` and `MG` Analyses as well:

    >>> sorted(new_analyses, key=methodcaller('getId'))
    [<Analysis at /plone/clients/client-1/water-0001-R01/CA>, <Analysis at /plone/clients/client-1/water-0001-R01/MG>]

In the Analyis Request should be now three Analyses:

    >>> len(ar.objectValues("Analysis"))
    3

Removing Analyses is done by omitting those from the `items` list:

    >>> new_analyses = field.set(ar, [analysisservice1])
    >>> sorted(new_analyses, key=methodcaller('getId'))
    []

Now there should be again only one Analysis assigned:

    >>> len(ar.objectValues("Analysis"))
    1

We expect to have just the `PH` Analysis again:

    >>> ar.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/water-0001-R01/PH>]

Removing all Analyses is prevented, because it can not be empty:

    >>> new_analyses = field.set(ar, [])
    >>> ar.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/water-0001-R01/PH>]

The field can also handle UIDs of Analyses Services:

    >>> service_uids = map(api.get_uid, all_services)
    >>> new_analyses = field.set(ar, service_uids)

We expect again to have the `CA` and `MG` Analyses as well:

    >>> sorted(new_analyses, key=methodcaller('getId'))
    [<Analysis at /plone/clients/client-1/water-0001-R01/CA>, <Analysis at /plone/clients/client-1/water-0001-R01/MG>]

And all the three Analyses in total:

    >>> sorted(ar.objectValues("Analysis"), key=methodcaller("getId"))
    [<Analysis at /plone/clients/client-1/water-0001-R01/CA>, <Analysis at /plone/clients/client-1/water-0001-R01/MG>, <Analysis at /plone/clients/client-1/water-0001-R01/PH>]

Set again only the `PH` Analysis:

    >>> new_analyses = field.set(ar, [analysisservice1])
    >>> ar.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/water-0001-R01/PH>]

The field should also handle catalog brains:

    >>> brains = api.search({"portal_type": "AnalysisService", "getKeyword": "CA"})
    >>> brains
    [<Products.ZCatalog.Catalog.mybrains object at 0x...>]

    >>> brain = brains[0]
    >>> api.get_title(brain)
    'Calcium'

    >>> new_analyses = field.set(ar, [brain])

We expect now to have just the `CA` analysis assigned:

    >>> ar.objectValues("Analysis")
    [<Analysis at /plone/clients/client-1/water-0001-R01/CA>]

Now let's try int mixed, one catalog brain and one object:

    >>> new_analyses = field.set(ar, [analysisservice1, brain])

We expect now to have now `PH` and `CA`:

    >>> sorted(ar.objectValues("Analysis"), key=methodcaller("getId"))
    [<Analysis at /plone/clients/client-1/water-0001-R01/CA>, <Analysis at /plone/clients/client-1/water-0001-R01/PH>]

Finally, we test it with an `Analysis` object:

    >>> analysis1 = ar["PH"]
    >>> new_analyses = field.set(ar, [analysis1])

    >>> sorted(ar.objectValues("Analysis"), key=methodcaller("getId"))
    [<Analysis at /plone/clients/client-1/water-0001-R01/PH>]


Setting Analysis Specifications
...............................

Specifications are defined on the `ResultsRange` field of an Analysis Request.
It is a dictionary with the following keys and values:

    - keyword: The Keyword of the Analysis Service
    - min: The minimum allowed value
    - max: The maximum allowed value
    - error: The error percentage
    - hidemin: ?
    - hidemax: ?
    - rangecomment: ?

Each Analysis can request its own Specification (Result Range):

    >>> new_analyses = field.set(ar, all_services)

    >>> analysis1 = ar[analysisservice1.getKeyword()]
    >>> analysis2 = ar[analysisservice2.getKeyword()]
    >>> analysis3 = ar[analysisservice3.getKeyword()]

The precedence of Specification lookup is AR -> Client -> Lab. Therefore, we
expect to get the prior added Water Specification of the Lab for each Analysis.

    >>> spec1 = analysis1.getResultsRange()
    >>> spec1.get("rangecomment")
    'Lab PH Spec'

    >>> spec2 = analysis2.getResultsRange()
    >>> spec2.get("rangecomment")
    'Lab MG Spec'

    >>> spec3 = analysis3.getResultsRange()
    >>> spec3.get("rangecomment")
    'Lab CA Spec'

Now we will set the analyses with custom specifications through the
ARAnalysesField. This should set the custom Specifications on the Analysis
Request and have precedence over the lab specifications:

    >>> arr1 = {"keyword": "PH", "min": 5.5, "max": 7.5, "error": 5, "hidemin": "", "hidemax": "", "rangecomment": "My PH Spec"}
    >>> arr2 = {"keyword": "MG", "min": 5.5, "max": 7.5, "error": 5, "hidemin": "", "hidemax": "", "rangecomment": "My MG Spec"}
    >>> arr3 = {"keyword": "CA", "min": 5.5, "max": 7.5, "error": 5, "hidemin": "", "hidemax": "", "rangecomment": "My CA Spec"}
    >>> arr = [arr1, arr2, arr3]

    >>> all_analyses = [analysis1, analysis2, analysis3]
    >>> new_analyses = field.set(ar, all_analyses, specs=arr)

    >>> myspec1 = analysis1.getResultsRange()
    >>> myspec1.get("rangecomment")
    'My PH Spec'

    >>> myspec2 = analysis2.getResultsRange()
    >>> myspec2.get("rangecomment")
    'My MG Spec'

    >>> myspec3 = analysis3.getResultsRange()
    >>> myspec3.get("rangecomment")
    'My CA Spec'

All Result Ranges are set on the AR:

    >>> sorted(map(lambda r: r.get("rangecomment"), ar.getResultsRange()))
    ['My CA Spec', 'My MG Spec', 'My PH Spec']

Now we simulate the form input data of the ARs "Manage Analysis" form, so that
the User only selected the `PH` service and gave some custom specifications for
this Analysis.

The specifications get applied if the keyword matches:

    >>> ph_specs = {"keyword": analysis1.getKeyword(), "min": 5.2, "max": 7.9, "error": 3}
    >>> new_analyses = field.set(ar, [analysis1], specs=[ph_specs])

We expect to have now just one Analysis set:

    >>> analyses = field.get(ar, full_objects=True)
    >>> analyses
    [<Analysis at /plone/clients/client-1/water-0001-R01/PH>]

And the specification should be according to the values we have set

    >>> ph = analyses[0]
    >>> phspec = ph.getResultsRange()

    >>> phspec.get("min")
    5.2

    >>> phspec.get("max")
    7.9

    >>> phspec.get("error")
    3


Setting Analyses Prices
.......................

Prices are primarily defined on Analyses Services:

    >>> analysisservice1.getPrice()
    '10.00'

    >>> analysisservice2.getPrice()
    '20.00'

    >>> analysisservice3.getPrice()
    '30.00'

Created Analyses inherit that price:

    >>> new_analyses = field.set(ar, all_services)

    >>> analysis1 = ar[analysisservice1.getKeyword()]
    >>> analysis2 = ar[analysisservice2.getKeyword()]
    >>> analysis3 = ar[analysisservice3.getKeyword()]

    >>> analysis1.getPrice()
    '10.00'

    >>> analysis2.getPrice()
    '20.00'

    >>> analysis3.getPrice()
    '30.00'

The `setter` also allows to set custom prices for the Analyses:

    >>> prices = {
    ...     analysisservice1.UID(): "100",
    ...     analysisservice2.UID(): "200",
    ...     analysisservice3.UID(): "300",
    ... }

Now we set the field with all analyses services and new prices:

    >>> new_analyses = field.set(ar, all_services, prices=prices)

The Analyses have now the new prices:

    >>> analysis1.getPrice()
    '100.00'

    >>> analysis2.getPrice()
    '200.00'

    >>> analysis3.getPrice()
    '300.00'

The Services should retain the old prices:

    >>> analysisservice1.getPrice()
    '10.00'

    >>> analysisservice2.getPrice()
    '20.00'

    >>> analysisservice3.getPrice()
    '30.00'


Calculations and Interim Fields
...............................

When an Analysis is assigned to an AR, it inherits its Calculation and Interim Fields.

Create some interim fields:

    >>> interim1 = {"keyword": "A", "title": "Interim A", "value": 1, "hidden": False, "type": "int", "unit": "x"}
    >>> interim2 = {"keyword": "B", "title": "Interim B", "value": 2, "hidden": False, "type": "int", "unit": "x"}
    >>> interim3 = {"keyword": "C", "title": "Interim C", "value": 3, "hidden": False, "type": "int", "unit": "x"}
    >>> interim4 = {"keyword": "D", "title": "Interim D", "value": 4, "hidden": False, "type": "int", "unit": "x"}

Append interim field `A` to the `Total Hardness` Calculation:

    >>> calc4.setInterimFields([interim1])
    >>> map(lambda x: x["keyword"], calc4.getInterimFields())
    ['A']

Append interim field `B` to the `Total Hardness` Analysis Service:

    >>> analysisservice4.setInterimFields([interim2])
    >>> map(lambda x: x["keyword"], analysisservice4.getInterimFields())
    ['B']

Now we assign the `Total Hardness` Analysis Service:

    >>> new_analyses = field.set(ar, [analysisservice4])
    >>> analysis = new_analyses[0]
    >>> analysis
    <Analysis at /plone/clients/client-1/water-0001-R01/THCaCO3>

The created Analysis has the same Calculation attached, as the Analysis Service:

    >>> analysis_calc = analysis.getCalculation()
    >>> analysis_calc
    <Calculation at /plone/bika_setup/bika_calculations/calculation-4>

And therofore, also the same Interim Fields as the Calculation:

    >>> map(lambda x: x["keyword"], analysis_calc.getInterimFields())
    ['A']

The Analysis also inherits the Interim Fields of the Analysis Service:

    >>> map(lambda x: x["keyword"], analysis.getInterimFields())
    ['B']

But what happens if the Interim Fields of either the Analysis Service or of the
Calculation change and the AR is updated with the same Analysis Service?

Change the Interim Field of the Calculation to `C`:

    >>> calc4.setInterimFields([interim3])
    >>> map(lambda x: x["keyword"], calc4.getInterimFields())
    ['C']

Change the Interim Fields of the Analysis Service to `D`:

    >>> analysisservice4.setInterimFields([interim4])
    >>> map(lambda x: x["keyword"], analysisservice4.getInterimFields())
    ['D']

Update the AR with the new Analysis Service:

    >>> new_analyses = field.set(ar, [analysisservice4])

Since no new Analyses were created, the field should return an empty list:

    >>> new_analyses
    []

The Analysis should be still there:

    >>> analysis = ar[analysisservice4.getKeyword()]
    >>> analysis
    <Analysis at /plone/clients/client-1/water-0001-R01/THCaCO3>

The calculation should be still there:

    >>> analysis_calc = analysis.getCalculation()
    >>> analysis_calc
    <Calculation at /plone/bika_setup/bika_calculations/calculation-4>

And therefore, also the same Interim Fields as the Calculation:

    >>> map(lambda x: x["keyword"], analysis_calc.getInterimFields())
    ['C']

The existing Analysis retains the initial Interim Fields of the Analysis Service:

    >>> map(lambda x: x["keyword"], analysis.getInterimFields())
    ['B']


Worksheets
..........

If the an Analysis is assigned to a worksheet, it should be detached before it
is removed from an Analysis Request.

Assign the `PH` Analysis:

    >>> new_analyses = field.set(ar, [analysisservice1])
    >>> new_analyses
    [<Analysis at /plone/clients/client-1/water-0001-R01/PH>]

Create a new Worksheet and assign the Analysis to it:

    >>> ws = api.create(worksheets, "Worksheet", "WS")
    >>> analysis = new_analyses[0]
    >>> ws.addAnalysis(analysis)

The analysis should be now in the 'assigned' state:

    >>> api.get_workflow_status_of(analysis, state_var='worksheetanalysis_review_state')
    'assigned'

The worksheet has now the Analysis assigned:

    >>> ws.getAnalyses()
    [<Analysis at /plone/clients/client-1/water-0001-R01/PH>]

Removing the analysis from the AR also unassignes it from the worksheet:

    >>> new_analyses = field.set(ar, [analysisservice2])
    >>> new_analyses
    [<Analysis at /plone/clients/client-1/water-0001-R01/MG>]

    >>> ws.getAnalyses()
    []


Dependencies
............

The Analysis Service `Total Hardness` uses the `Total Hardness` Calculation:

    >>> analysisservice4.getCalculation()
    <Calculation at /plone/bika_setup/bika_calculations/calculation-4>

The Calculation is dependent on the `CA` and `MG` Services through its Formula:

    >>> analysisservice4.getCalculation().getFormula()
    '[CA] + [MG]'

Get the dependent services:

    >>> sorted(analysisservice4.getServiceDependencies(), key=methodcaller('getId'))
    [<AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-2>, <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-3>]

We expect that dependent services get automatically set:

    >>> new_analyses = field.set(ar, [analysisservice4], debug=1)

    >>> sorted(ar.objectValues("Analysis"), key=methodcaller('getId'))
    [<Analysis at /plone/clients/client-1/water-0001-R01/CA>, <Analysis at /plone/clients/client-1/water-0001-R01/MG>, <Analysis at /plone/clients/client-1/water-0001-R01/THCaCO3>]
