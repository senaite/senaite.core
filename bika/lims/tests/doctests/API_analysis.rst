API Analysis
============

Th> api_analysis provides single functions for single purposes especifically
related with analyses.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t API_analysis


Test Setup
----------

Needed Imports:

    >>> import re
    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.api.analysis import is_out_of_range
    >>> from bika.lims.content.analysisrequest import AnalysisRequest
    >>> from bika.lims.content.sample import Sample
    >>> from bika.lims.content.samplepartition import SamplePartition
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.sample import create_sample
    >>> from bika.lims.utils import tmpID
    >>> from bika.lims.workflow import doActionFor
    >>> from bika.lims.workflow import getCurrentState
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from DateTime import DateTime
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from plone.app.testing import setRoles

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> bikasetup = portal.bika_setup

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(bikasetup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(bikasetup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(bikasetup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> supplier = api.create(bikasetup.bika_suppliers, "Supplier", Name="Naralabs")
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), DuplicateVariation="0.5")
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID(), DuplicateVariation="0.5")
    >>> Au = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID(), DuplicateVariation="0.5")
    >>> Mg = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Magnesium", Keyword="Mg", Price="20", Category=category.UID(), DuplicateVariation="0.5")
    >>> service_uids = [api.get_uid(an) for an in [Cu, Fe, Au, Mg]]

Create an Analysis Specification for `Water`:

    >>> sampletype_uid = api.get_uid(sampletype)
    >>> rr1 = {"keyword": "Au", "min": "-5", "max":  "5", "warn_min": "-5.5", "warn_max": "5.5"}
    >>> rr2 = {"keyword": "Cu", "min": "10", "max": "20", "warn_min":  "9.5", "warn_max": "20.5"}
    >>> rr3 = {"keyword": "Fe", "min":  "0", "max": "10", "warn_min": "-0.5", "warn_max": "10.5"}
    >>> rr4 = {"keyword": "Mg", "min": "10", "max": "10"}
    >>> rr = [rr1, rr2, rr3, rr4]
    >>> specification = api.create(bikasetup.bika_analysisspecs, "AnalysisSpec", title="Lab Water Spec", SampleType=sampletype_uid, ResultsRange=rr)
    >>> spec_uid = api.get_uid(specification)

Create a Reference Definition for blank:

    >>> blankdef = api.create(bikasetup.bika_referencedefinitions, "ReferenceDefinition", title="Blank definition", Blank=True)
    >>> blank_refs = [{'uid': Au.UID(), 'result': '0', 'min': '0', 'max': '0', 'error': '0'},
    ...               {'uid': Cu.UID(), 'result': '0', 'min': '0', 'max': '0', 'error': '0'},
    ...               {'uid': Fe.UID(), 'result': '0', 'min': '0', 'max': '0', 'error': '0'},
    ...               {'uid': Mg.UID(), 'result': '0', 'min': '0', 'max': '0', 'error': '0'},]
    >>> blankdef.setReferenceResults(blank_refs)

And for control:

    >>> controldef = api.create(bikasetup.bika_referencedefinitions, "ReferenceDefinition", title="Control definition")
    >>> control_refs = [{'uid': Au.UID(), 'result': '10', 'min': '0.9', 'max': '10.1', 'error': '0.1'},
    ...                 {'uid': Cu.UID(), 'result': '10', 'min': '0.9', 'max': '10.1', 'error': '0.1'},
    ...                 {'uid': Fe.UID(), 'result': '10', 'min': '0.9', 'max': '10.1', 'error': '0.1'},
    ...                 {'uid': Mg.UID(), 'result': '10', 'min': '0.9', 'max': '10.1', 'error': '0.1'}]
    >>> controldef.setReferenceResults(control_refs)

    >>> blank = api.create(supplier, "ReferenceSample", title="Blank",
    ...                    ReferenceDefinition=blankdef,
    ...                    Blank=True, ExpiryDate=date_future,
    ...                    ReferenceResults=blank_refs)
    >>> control = api.create(supplier, "ReferenceSample", title="Control",
    ...                      ReferenceDefinition=controldef,
    ...                      Blank=False, ExpiryDate=date_future,
    ...                      ReferenceResults=control_refs)

Create an Analysis Request:

    >>> values = {
    ...     'Client': api.get_uid(client),
    ...     'Contact': api.get_uid(contact),
    ...     'DateSampled': date_now,
    ...     'SampleType': sampletype_uid,
    ...     'Specification': spec_uid,
    ...     'Priority': '1',
    ... }

    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> success = doActionFor(ar, 'receive')

Create a new Worksheet and add the analyses:

    >>> worksheet = api.create(portal.worksheets, "Worksheet")
    >>> analyses = [api.get_object(an) for an  in ar.getAnalyses()]
    >>> for analysis in analyses:
    ...     worksheet.addAnalysis(analysis)

Add a duplicate for `Cu`:

    >>> position = worksheet.get_slot_position(ar, 'a')
    >>> duplicates = worksheet.addDuplicateAnalyses(position)
    >>> duplicates.sort(key=lambda analysis: analysis.getKeyword(), reverse=False)

Add a blank and a control:

    >>> blanks = worksheet.addReferenceAnalyses(blank, service_uids)
    >>> blanks.sort(key=lambda analysis: analysis.getKeyword(), reverse=False)
    >>> controls = worksheet.addReferenceAnalyses(control, service_uids)
    >>> controls.sort(key=lambda analysis: analysis.getKeyword(), reverse=False)


Check if results are out of range
---------------------------------

First, get the analyses from slot 1 and sort them asc:

    >>> analyses = worksheet.get_analyses_at(1)
    >>> analyses.sort(key=lambda analysis: analysis.getKeyword(), reverse=False)

Set results for analysis `Au` (min: -5, max: 5, warn_min: -5.5, warn_max: 5.5):

    >>> au_analysis = analyses[0]
    >>> au_analysis.setResult(2)
    >>> is_out_of_range(au_analysis)
    (False, False)

    >>> au_analysis.setResult(-2)
    >>> is_out_of_range(au_analysis)
    (False, False)

    >>> au_analysis.setResult(-5)
    >>> is_out_of_range(au_analysis)
    (False, False)

    >>> au_analysis.setResult(5)
    >>> is_out_of_range(au_analysis)
    (False, False)

    >>> au_analysis.setResult(10)
    >>> is_out_of_range(au_analysis)
    (True, True)

    >>> au_analysis.setResult(-10)
    >>> is_out_of_range(au_analysis)
    (True, True)

Results in shoulders?:

    >>> au_analysis.setResult(-5.2)
    >>> is_out_of_range(au_analysis)
    (True, False)

    >>> au_analysis.setResult(-5.5)
    >>> is_out_of_range(au_analysis)
    (True, False)

    >>> au_analysis.setResult(-5.6)
    >>> is_out_of_range(au_analysis)
    (True, True)

    >>> au_analysis.setResult(5.2)
    >>> is_out_of_range(au_analysis)
    (True, False)

    >>> au_analysis.setResult(5.5)
    >>> is_out_of_range(au_analysis)
    (True, False)

    >>> au_analysis.setResult(5.6)
    >>> is_out_of_range(au_analysis)
    (True, True)


Check if results for duplicates are out of range
------------------------------------------------

Get the first duplicate analysis that comes from from `Au`:

    >>> duplicate = duplicates[0]

A Duplicate will be considered out of range if its result does not match with
the result set to the analysis that was duplicated from, with the Duplicate
Variation in % as the margin error. The Duplicate Variation assigned in the
Analysis Service `Au` is 0.5%:

    >>> dup_variation = au_analysis.getDuplicateVariation()
    >>> dup_variation = api.to_float(dup_variation)
    >>> dup_variation
    0.5

Set an in-range result (between -5 and 5) for routine analysis and check all
variants on it's duplicate. Given that the duplicate variation is 0.5, the
valid range for the duplicate must be `Au +-0.5%`:

    >>> result = 2.0
    >>> au_analysis.setResult(result)
    >>> is_out_of_range(au_analysis)
    (False, False)

    >>> duplicate.setResult(result)
    >>> is_out_of_range(duplicate)
    (False, False)

    >>> dup_min_range = result - (result*(dup_variation/100))
    >>> duplicate.setResult(dup_min_range)
    >>> is_out_of_range(duplicate)
    (False, False)

    >>> duplicate.setResult(dup_min_range - 0.5)
    >>> is_out_of_range(duplicate)
    (True, True)

    >>> dup_max_range = result + (result*(dup_variation/100))
    >>> duplicate.setResult(dup_max_range)
    >>> is_out_of_range(duplicate)
    (False, False)

    >>> duplicate.setResult(dup_max_range + 0.5)
    >>> is_out_of_range(duplicate)
    (True, True)

Set an out-of-range result, but within shoulders, for routine analysis and check
all variants on it's duplicate. Given that the duplicate variation is 0.5, the
valid range for the duplicate must be `Au +-0.5%`:

    >>> result = 5.5
    >>> au_analysis.setResult(result)
    >>> is_out_of_range(au_analysis)
    (True, False)

    >>> duplicate.setResult(result)
    >>> is_out_of_range(duplicate)
    (False, False)

    >>> dup_min_range = result - (result*(dup_variation/100))
    >>> duplicate.setResult(dup_min_range)
    >>> is_out_of_range(duplicate)
    (False, False)

    >>> duplicate.setResult(dup_min_range - 0.5)
    >>> is_out_of_range(duplicate)
    (True, True)

    >>> dup_max_range = result + (result*(dup_variation/100))
    >>> duplicate.setResult(dup_max_range)
    >>> is_out_of_range(duplicate)
    (False, False)

    >>> duplicate.setResult(dup_max_range + 0.5)
    >>> is_out_of_range(duplicate)
    (True, True)

Set an out-of-range and out-of-shoulders result, for routine analysis and check
all variants on it's duplicate. Given that the duplicate variation is 0.5, the
valid range for the duplicate must be `Au +-0.5%`:

    >>> result = -7.0
    >>> au_analysis.setResult(result)
    >>> is_out_of_range(au_analysis)
    (True, True)

    >>> duplicate.setResult(result)
    >>> is_out_of_range(duplicate)
    (False, False)

    >>> dup_min_range = result - (abs(result)*(dup_variation/100))
    >>> duplicate.setResult(dup_min_range)
    >>> is_out_of_range(duplicate)
    (False, False)

    >>> duplicate.setResult(dup_min_range - 0.5)
    >>> is_out_of_range(duplicate)
    (True, True)

    >>> dup_max_range = result + (abs(result)*(dup_variation/100))
    >>> duplicate.setResult(dup_max_range)
    >>> is_out_of_range(duplicate)
    (False, False)

    >>> duplicate.setResult(dup_max_range + 0.5)
    >>> is_out_of_range(duplicate)
    (True, True)
