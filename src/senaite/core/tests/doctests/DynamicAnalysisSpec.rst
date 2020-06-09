Dynamic Analysis Specifications
===============================

A *Dynamic Analysis Specification* can be assigned to *Analysis Specifications*.

When retrieving the result ranges (specification) for an Analysis, a lookup is
done on the *Dynamic Analysis Specification*.

Example
-------

Given is an Excel with the following minimal set of columns:

======= ======== === ===
Keyword Method   min max
======= ======== === ===
Ca      Method A 1   2
Ca      Method B 3   4
Mg      Method A 5   6
Mg      Method B 7   8
======= ======== === ===

This Excel is uploaded to an *Dynamic Analysis Specification* object, which is
linked to an Analysis Specification for the Sample Type "Water".

A new "Water" Sample is created with an containing `H2O` analysis to be tested
with `Method-2`. The results range selected will be `[3;4]`.


Running this test from the buildout directory:

    bin/test test_textual_doctests -t DynamicAnalysisSpec.rst

Test Setup
----------

Needed imports:

    >>> from DateTime import DateTime
    >>> from StringIO import StringIO
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from openpyxl import Workbook
    >>> from openpyxl.writer.excel import save_virtual_workbook
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> from plone.namedfile.file import NamedBlobFile
    >>> import csv

Some Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_setup()

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
    ...     ar = create_analysisrequest(client, request, values)
    ...     transitioned = do_action_for(ar, "receive")
    ...     return ar

Privileges:

    >>> setRoles(portal, TEST_USER_ID, ['Manager',])


Creating a Dynamic Analysis Specification
-----------------------------------------

Dynamic Analysis Specifications are actually only small wrappers around an Excel
file, where result ranges are defined per row.

Let's create first a small helper function that generates an Excel for us:

    >>> def to_excel(data):
    ...     workbook = Workbook()
    ...     first_sheet = workbook.get_active_sheet()
    ...     reader = csv.reader(StringIO(data))
    ...     for row in reader:
    ...         first_sheet.append(row)
    ...     return NamedBlobFile(save_virtual_workbook(workbook))

Then we create the data according to the example given above:

    >>> data = """Keyword,Method,min,max
    ... Ca,Method A,1,2
    ... Ca,Method B,3,4
    ... Mg,Method A,5,6
    ... Mg,Method B,7,8"""

Now we can create a Dynamic Analysis Specification Object:

    >>> ds = api.create(setup.dynamic_analysisspecs, "DynamicAnalysisSpec")
    >>> ds.specs_file = to_excel(data)

We can get now directly the parsed header:

    >>> header = ds.get_header()
    >>> header
    [u'Keyword', u'Method', u'min', u'max']

And the result ranges:

    >>> rr = ds.get_specs()
    >>> map(lambda r: [r.get(k) for k in header], rr)
    [[u'Ca', u'Method A', 1, 2], [u'Ca', u'Method B', 3, 4], [u'Mg', u'Method A', 5, 6], [u'Mg', u'Method B', 7, 8]]

We can also get the specs by Keyword:

    >>> mg_rr = ds.get_by_keyword()["Mg"]
    >>> map(lambda r: [r.get(k) for k in header], mg_rr)
    [[u'Mg', u'Method A', 5, 6], [u'Mg', u'Method B', 7, 8]]


Hooking in a Dynamic Analysis Specification
-------------------------------------------

Dynamic Analysis Specifications can only be assigned to a default Analysis Specification.

First we build some basic setup structure:

    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> labcontact = api.create(setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)

    >>> method_a = api.create(portal.methods, "Method", title="Method A")
    >>> method_b = api.create(portal.methods, "Method", title="Method B")

    >>> Ca = api.create(setup.bika_analysisservices, "AnalysisService", title="Calcium", Keyword="Ca", Category=category, Method=method_a)
    >>> Mg = api.create(setup.bika_analysisservices, "AnalysisService", title="Magnesium", Keyword="Mg", Category=category, Method=method_a)

Then we create a default Analysis Specification:

    >>> rr1 = {"keyword": "Ca", "min": 10, "max": 20, "warn_min": 9, "warn_max": 21}
    >>> rr2 = {"keyword": "Mg", "min": 10, "max": 20, "warn_min": 9, "warn_max": 21}
    >>> sampletype = api.create(setup.bika_sampletypes, "SampleType", title="Water", Prefix="H2O")
    >>> specification = api.create(setup.bika_analysisspecs, "AnalysisSpec", title="Lab Water Spec", SampleType=sampletype.UID(), ResultsRange=[rr1, rr2])

And create a new sample with the given Analyses and the Specification:

    >>> services = [Ca, Mg]
    >>> sample = new_sample(services, specification=specification)
    >>> ca, mg = sample["Ca"], sample["Mg"]

The specification is according to the values we have set before:

    >>> ca_spec = ca.getResultsRange()
    >>> ca_spec["min"], ca_spec["max"]
    (10, 20)

    >>> mg_spec = mg.getResultsRange()
    >>> mg_spec["min"], mg_spec["max"]
    (10, 20)

Now we hook in our Dynamic Analysis Specification to the standard Specification:

    >>> specification.setDynamicAnalysisSpec(ds)


The specification need to get unset/set again, so that the dynamic values get looked up:

    >>> sample.setSpecification(None)
    >>> sample.setSpecification(specification)

The specification of the `Ca` Analysis with the Method `Method A`:

    >>> ca_spec = ca.getResultsRange()
    >>> ca_spec["min"], ca_spec["max"]
    (1, 2)

Now let's change the `Ca` Analysis Method to `Method B`:

    >>> ca.setMethod(method_b)

Unset and set the specification again:

    >>> sample.setSpecification(None)
    >>> sample.setSpecification(specification)

And get the results range again:

    >>> ca_spec = ca.getResultsRange()
    >>> ca_spec["min"], ca_spec["max"]
    (3, 4)

The same now with the `Mg` Analysis in one run:

    >>> mg_spec = mg.getResultsRange()
    >>> mg_spec["min"], mg_spec["max"]
    (5, 6)

    >>> mg.setMethod(method_b)

Unset and set the specification again:

    >>> sample.setSpecification(None)
    >>> sample.setSpecification(specification)

    >>> mg_spec = mg.getResultsRange()
    >>> mg_spec["min"], mg_spec["max"]
    (7, 8)
