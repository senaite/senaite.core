API Analysis
============

The api_analysis provides single functions for single purposes especifically
related with analyses.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t API_analysis


Test Setup
----------

Needed Imports:

    >>> import re
    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.api.analysis import get_formatted_interval
    >>> from bika.lims.api.analysis import is_out_of_range
    >>> from bika.lims.content.analysisrequest import AnalysisRequest
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
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
    >>> blank_refs = [{'uid': Au.UID(), 'result': '0', 'min': '0', 'max': '0'},]
    >>> blankdef.setReferenceResults(blank_refs)

And for control:

    >>> controldef = api.create(bikasetup.bika_referencedefinitions, "ReferenceDefinition", title="Control definition")
    >>> control_refs = [{'uid': Au.UID(), 'result': '10', 'min': '9.99', 'max': '10.01'},
    ...                 {'uid': Cu.UID(), 'result': '-0.9','min': '-1.08', 'max': '-0.72'},]
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
    >>> analyses = map(api.get_object, ar.getAnalyses())
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

Get the first duplicate analysis that comes from `Au`:

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


Check if results for Reference Analyses (blanks + controls) are out of range
----------------------------------------------------------------------------

Reference Analyses (controls and blanks) do not use the result ranges defined in
the specifications, rather they use the result range defined in the Reference
Sample they have been generated from. In turn, the result ranges defined in
Reference Samples can be set manually or acquired from the Reference Definition
they might be associated with. Another difference from routine analyses is that
reference analyses don't expect a valid range, rather a discrete value, so
shoulders are built based on % error.

Blank Analyses
..............

The first blank analysis corresponds to `Au`:

    >>> au_blank = blanks[0]

For `Au` blank, as per the reference definition used above, the expected result
is 0 +/- 0.1%. Since the expected result is 0, no shoulders will be considered
regardless of the % of error. Thus, result will always be "out-of-shoulders"
when out of range.

    >>> au_blank.setResult(0.0)
    >>> is_out_of_range(au_blank)
    (False, False)

    >>> au_blank.setResult("0")
    >>> is_out_of_range(au_blank)
    (False, False)

    >>> au_blank.setResult(0.0001)
    >>> is_out_of_range(au_blank)
    (True, True)

    >>> au_blank.setResult("0.0001")
    >>> is_out_of_range(au_blank)
    (True, True)

    >>> au_blank.setResult(-0.0001)
    >>> is_out_of_range(au_blank)
    (True, True)

    >>> au_blank.setResult("-0.0001")
    >>> is_out_of_range(au_blank)
    (True, True)

Control Analyses
................

The first control analysis corresponds to `Au`:

    >>> au_control = controls[0]

For `Au` control, as per the reference definition used above, the expected
result is 10 +/- 0.1% = 10 +/- 0.01

First, check for in-range values:

    >>> au_control.setResult(10)
    >>> is_out_of_range(au_control)
    (False, False)

    >>> au_control.setResult(10.0)
    >>> is_out_of_range(au_control)
    (False, False)

    >>> au_control.setResult("10")
    >>> is_out_of_range(au_control)
    (False, False)

    >>> au_control.setResult("10.0")
    >>> is_out_of_range(au_control)
    (False, False)

    >>> au_control.setResult(9.995)
    >>> is_out_of_range(au_control)
    (False, False)

    >>> au_control.setResult("9.995")
    >>> is_out_of_range(au_control)
    (False, False)

    >>> au_control.setResult(10.005)
    >>> is_out_of_range(au_control)
    (False, False)

    >>> au_control.setResult("10.005")
    >>> is_out_of_range(au_control)
    (False, False)

    >>> au_control.setResult(9.99)
    >>> is_out_of_range(au_control)
    (False, False)

    >>> au_control.setResult("9.99")
    >>> is_out_of_range(au_control)
    (False, False)

    >>> au_control.setResult(10.01)
    >>> is_out_of_range(au_control)
    (False, False)

    >>> au_control.setResult("10.01")
    >>> is_out_of_range(au_control)
    (False, False)

Now, check for out-of-range results:

    >>> au_control.setResult(9.98)
    >>> is_out_of_range(au_control)
    (True, True)

    >>> au_control.setResult("9.98")
    >>> is_out_of_range(au_control)
    (True, True)

    >>> au_control.setResult(10.011)
    >>> is_out_of_range(au_control)
    (True, True)

    >>> au_control.setResult("10.011")
    >>> is_out_of_range(au_control)
    (True, True)

And do the same with the control for `Cu` that expects -0.9 +/- 20%:

    >>> cu_control = controls[1]

First, check for in-range values:

    >>> cu_control.setResult(-0.9)
    >>> is_out_of_range(cu_control)
    (False, False)

    >>> cu_control.setResult("-0.9")
    >>> is_out_of_range(cu_control)
    (False, False)

    >>> cu_control.setResult(-1.08)
    >>> is_out_of_range(cu_control)
    (False, False)

    >>> cu_control.setResult("-1.08")
    >>> is_out_of_range(cu_control)
    (False, False)

    >>> cu_control.setResult(-1.07)
    >>> is_out_of_range(cu_control)
    (False, False)

    >>> cu_control.setResult("-1.07")
    >>> is_out_of_range(cu_control)
    (False, False)

    >>> cu_control.setResult(-0.72)
    >>> is_out_of_range(cu_control)
    (False, False)

    >>> cu_control.setResult("-0.72")
    >>> is_out_of_range(cu_control)
    (False, False)

    >>> cu_control.setResult(-0.73)
    >>> is_out_of_range(cu_control)
    (False, False)

    >>> cu_control.setResult("-0.73")
    >>> is_out_of_range(cu_control)
    (False, False)

Now, check for out-of-range results:

    >>> cu_control.setResult(0)
    >>> is_out_of_range(cu_control)
    (True, True)

    >>> cu_control.setResult("0")
    >>> is_out_of_range(cu_control)
    (True, True)

    >>> cu_control.setResult(-0.71)
    >>> is_out_of_range(cu_control)
    (True, True)

    >>> cu_control.setResult("-0.71")
    >>> is_out_of_range(cu_control)
    (True, True)

    >>> cu_control.setResult(-1.09)
    >>> is_out_of_range(cu_control)
    (True, True)

    >>> cu_control.setResult("-1.09")
    >>> is_out_of_range(cu_control)
    (True, True)


Check if results are out of range when open interval is used
------------------------------------------------------------

Set open interval for min and max from water specification

    >>> ranges = specification.getResultsRange()
    >>> for range in ranges:
    ...     range['min_operator'] = 'gt'
    ...     range['max_operator'] = 'lt'
    >>> specification.setResultsRange(ranges)

We need to re-apply the Specification for the changes to take effect:

    >>> ar.setSpecification(None)
    >>> ar.setSpecification(specification)

First, get the analyses from slot 1 and sort them asc:

    >>> analyses = worksheet.get_analyses_at(1)
    >>> analyses.sort(key=lambda analysis: analysis.getKeyword(), reverse=False)

Set results for analysis `Au` (min: -5, max: 5, warn_min: -5.5, warn_max: 5.5):

    >>> au_analysis = analyses[0]
    >>> au_analysis.setResult(-5)
    >>> is_out_of_range(au_analysis)
    (True, False)

    >>> au_analysis.setResult(5)
    >>> is_out_of_range(au_analysis)
    (True, False)


Check if results are out of range when left-open interval is used
-----------------------------------------------------------------

Set left-open interval for min and max from water specification

    >>> ranges = specification.getResultsRange()
    >>> for range in ranges:
    ...     range['min_operator'] = 'geq'
    ...     range['max_operator'] = 'lt'
    >>> specification.setResultsRange(ranges)

We need to re-apply the Specification for the changes to take effect:

    >>> ar.setSpecification(None)
    >>> ar.setSpecification(specification)

First, get the analyses from slot 1 and sort them asc:

    >>> analyses = worksheet.get_analyses_at(1)
    >>> analyses.sort(key=lambda analysis: analysis.getKeyword(), reverse=False)

Set results for analysis `Au` (min: -5, max: 5, warn_min: -5.5, warn_max: 5.5):

    >>> au_analysis = analyses[0]
    >>> au_analysis.setResult(-5)
    >>> is_out_of_range(au_analysis)
    (False, False)

    >>> au_analysis.setResult(5)
    >>> is_out_of_range(au_analysis)
    (True, False)


Check if results are out of range when right-open interval is used
------------------------------------------------------------------

Set right-open interval for min and max from water specification

    >>> ranges = specification.getResultsRange()
    >>> for range in ranges:
    ...     range['min_operator'] = 'gt'
    ...     range['max_operator'] = 'leq'
    >>> specification.setResultsRange(ranges)

We need to re-apply the Specification for the changes to take effect:

    >>> ar.setSpecification(None)
    >>> ar.setSpecification(specification)

First, get the analyses from slot 1 and sort them asc:

    >>> analyses = worksheet.get_analyses_at(1)
    >>> analyses.sort(key=lambda analysis: analysis.getKeyword(), reverse=False)

Set results for analysis `Au` (min: -5, max: 5, warn_min: -5.5, warn_max: 5.5):

    >>> au_analysis = analyses[0]
    >>> au_analysis.setResult(-5)
    >>> is_out_of_range(au_analysis)
    (True, False)

    >>> au_analysis.setResult(5)
    >>> is_out_of_range(au_analysis)
    (False, False)


Check if formatted interval is rendered properly
------------------------------------------------

Set closed interval for min and max from water specification

    >>> ranges = specification.getResultsRange()
    >>> for range in ranges:
    ...     range['min_operator'] = 'geq'
    ...     range['max_operator'] = 'leq'
    >>> specification.setResultsRange(ranges)

Get the result range for `Au` (min: -5, max: 5)

    >>> rr = specification.getResultsRange()
    >>> res_range = filter(lambda item: item.get('keyword') == 'Au', rr)[0]
    >>> get_formatted_interval(res_range)
    '[-5;5]'

Try now with left-open interval

    >>> ranges = specification.getResultsRange()
    >>> for range in ranges:
    ...     range['min_operator'] = 'gt'
    ...     range['max_operator'] = 'leq'
    >>> specification.setResultsRange(ranges)

Get the result range for `Au` (min: -5, max: 5)

    >>> rr = specification.getResultsRange()
    >>> res_range = filter(lambda item: item.get('keyword') == 'Au', rr)[0]
    >>> get_formatted_interval(res_range)
    '(-5;5]'

Try now with right-open interval

    >>> ranges = specification.getResultsRange()
    >>> for range in ranges:
    ...     range['min_operator'] = 'geq'
    ...     range['max_operator'] = 'lt'
    >>> specification.setResultsRange(ranges)

Get the result range for `Au` (min: -5, max: 5)

    >>> rr = specification.getResultsRange()
    >>> res_range = filter(lambda item: item.get('keyword') == 'Au', rr)[0]
    >>> get_formatted_interval(res_range)
    '[-5;5)'

Try now with open interval

    >>> ranges = specification.getResultsRange()
    >>> for range in ranges:
    ...     range['min_operator'] = 'gt'
    ...     range['max_operator'] = 'lt'
    >>> specification.setResultsRange(ranges)

Get the result range for `Au` (min: -5, max: 5)

    >>> rr = specification.getResultsRange()
    >>> res_range = filter(lambda item: item.get('keyword') == 'Au', rr)[0]
    >>> get_formatted_interval(res_range)
    '(-5;5)'

And if we set a 0 value as min or max?

    >>> res_range['min'] = 0
    >>> get_formatted_interval(res_range)
    '(0;5)'

    >>> res_range['max'] = 0
    >>> res_range['min'] = -5
    >>> get_formatted_interval(res_range)
    '(-5;0)'

And now, set no value for min and/or max

    >>> res_range['min'] = ''
    >>> res_range['max'] = 5
    >>> get_formatted_interval(res_range)
    '<5'

    >>> res_range['max'] = ''
    >>> res_range['min'] = -5
    >>> get_formatted_interval(res_range)
    '>-5'

And change the operators

    >>> res_range['min'] = ''
    >>> res_range['max'] = 5
    >>> res_range['max_operator'] = 'leq'
    >>> get_formatted_interval(res_range)
    '<=5'

    >>> res_range['max'] = ''
    >>> res_range['min'] = -5
    >>> res_range['max_operator'] = 'lt'
    >>> res_range['min_operator'] = 'geq'
    >>> get_formatted_interval(res_range)
    '>=-5'
