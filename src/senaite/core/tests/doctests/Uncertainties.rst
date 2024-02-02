Uncertainties
-------------

Since version 2.3 uncertainties are stored in a String field instead of a FixedPoint field.
This ensures that we always maintain the original (user entered) value in the database.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t Uncertainties


Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

    >>> def new_sample(services):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': date_now,
    ...         'SampleType': sampletype.UID()}
    ...     service_uids = map(api.get_uid, services)
    ...     ar = create_analysisrequest(client, request, values, service_uids)
    ...     transitioned = do_action_for(ar, "receive")
    ...     return ar

    >>> def get_analysis(sample, service):
    ...     service_uid = api.get_uid(service)
    ...     for analysis in sample.getAnalyses(full_objects=True):
    ...         if analysis.getServiceUID() == service_uid:
    ...             return analysis
    ...     return None

    >>> def submit_analyses(ar, result="13"):
    ...     for analysis in ar.getAnalyses(full_objects=True):
    ...         analysis.setResult(result)
    ...         do_action_for(analysis, "submit")

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = api.get_bika_setup()
    >>> date_now = DateTime().strftime("%Y-%m-%d")

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(bikasetup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(bikasetup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())


Test manual Uncertainty
.......................

We allow the user to enter a manual uncertainty value:

    >>> Cu.setAllowManualUncertainty(True)
    >>> Fe.setAllowManualUncertainty(True)
    >>> Au.setAllowManualUncertainty(True)

Create an Analysis Request and submit results:

    >>> sample = new_sample([Cu, Fe, Au])

    >>> cu = get_analysis(sample, Cu)
    >>> cu.getAllowManualUncertainty()
    True

    >>> fe = get_analysis(sample, Fe)
    >>> fe.getAllowManualUncertainty()
    True

    >>> au = get_analysis(sample, Au)
    >>> au.getAllowManualUncertainty()
    True

Enter manual uncertainties to the analyses:

    >>> cu.setUncertainty("0.2")
    >>> cu.getUncertainty()
    '0.2'

    >>> fe.setUncertainty("0.4")
    >>> fe.getUncertainty()
    '0.4'

We can also enter floats instead of strings:


    >>> au.setUncertainty(0.6)
    >>> au.getUncertainty()
    '0.6'


Test Uncertainty Ranges
.......................

Define some ranges with their specific ranges:

    >>> uncertainties = [
    ...    {"intercept_min":  0, "intercept_max":  5, "errorvalue": 0.0015},
    ...    {"intercept_min":  5, "intercept_max": 10, "errorvalue": 0.02},
    ...    {"intercept_min": 10, "intercept_max": 20, "errorvalue": 0.4},
    ... ]

Then we apply it to a service:

    >>> Au.setUncertainties(uncertainties)

Create a new sample with this service included:

    >>> sample = new_sample([Cu, Fe, Au])

    >>> au = get_analysis(sample, Au)
    >>> au.getAllowManualUncertainty()
    True

Test uncertainty range 1: 0-5 -> 0.0015

    >>> au.setResult(1)
    >>> au.getUncertainty()
    '0.0015'

Test uncertainty range 2: 5-10 -> 0.02

    >>> au.setResult(5.1)
    >>> au.getUncertainty()
    '0.02'

Test uncertainty range 3: 10-20 -> 0.4

    >>> au.setResult(20)
    >>> au.getUncertainty()
    '0.4'

Test uncertainty out of defined ranges:

    >>> au.setResult(100)
    >>> au.getUncertainty() is None
    True

Test overriding a uncertainty range:

    >>> au.setResult(1)
    >>> au.setUncertainty(0.1)
    >>> au.getUncertainty()
    '0.1'

Removing the manual uncertainty should give us the value from the range again:

    >>> au.setUncertainty(None)
    >>> au.getUncertainty()
    '0.0015'


Test precision from uncertainty
...............................

Setup the service to calculate precision from uncertainty:

    >>> Fe.setUncertainties(uncertainties)
    >>> Fe.setPrecisionFromUncertainty(True)

Create a new sample with this service included:

    >>> sample = new_sample([Cu, Fe, Au])

    >>> fe = get_analysis(sample, Fe)
    >>> fe.getPrecisionFromUncertainty()
    True

The formatted result should now have the precision of the uncertainty, which is
calculated by the significant digits of the uncertainty (in this case `3`):

    >>> from bika.lims.utils.analysis import get_significant_digits

    >>> get_significant_digits("0.0015")
    3

    >>> get_significant_digits("0.02")
    2

    >>> get_significant_digits("0.4")
    1

Check the precision of the range 0-5 (0.0015)

    >>> fe.setResult("2.3452")
    >>> fe.getResult()
    '2.3452'

    >>> fe.getUncertainty()
    '0.0015'

    >>> fe.getFormattedResult()
    '2.345'

Check the precision of the range 5-10 (0.02):

    >>> fe.setResult("5.3452")
    >>> fe.getResult()
    '5.3452'

    >>> fe.getUncertainty()
    '0.02'

    >>> fe.getFormattedResult()
    '5.35'

Check the precision of the range 10-20 (0.4):

    >>> fe.setResult("10.3452")
    >>> fe.getResult()
    '10.3452'

    >>> fe.getUncertainty()
    '0.4'

    >>> fe.getFormattedResult()
    '10.3'

Check the precision is calculated based on the rounded uncertainty:

    >>> uncertainties_2 = [
    ...    {'intercept_min': '1.0', 'intercept_max': '100000', 'errorvalue': '9.9%'},
    ...    {'intercept_min': '0.5', 'intercept_max': '0.9', 'errorvalue': '0'}
    ... ]
    >>> fe.setUncertainties(uncertainties_2)
    >>> fe.setResult("9.6")
    >>> fe.getResult()
    '9.6'

    >>> fe.getUncertainty()
    '0.9504'

    >>> fe.getPrecision()
    0

    >>> fe.getFormattedResult()
    '10'

Test uncertainty for results above/below detection limits
.........................................................

Setup uncertainty settings in the service:

    >>> Cu.setAllowManualUncertainty(True)
    >>> Cu.setUncertainties(uncertainties)
    >>> Cu.setPrecisionFromUncertainty(True)
    >>> Cu.setUpperDetectionLimit("21")
    >>> Cu.setLowerDetectionLimit("0")

    >>> sample = new_sample([Cu, Fe, Au])

    >>> cu = get_analysis(sample, Cu)

    >>> cu.setResult("25.3452")
    >>> cu.getResult()
    '25.3452'

    >>> cu.getUncertainty() is None
    True

    >>> cu.isAboveUpperDetectionLimit()
    True

The uncertainty is also `None` when set manually if the result is above UDL:

    >>> cu.setUncertainty("0.5")
    >>> cu.getUncertainty() is None
    True

The same happens when the result is below UDL

    >>> cu.setResult("-1")
    >>> cu.getResult()
    '-1'

    >>> cu.getUncertainty() is None
    True

    >>> cu.isBelowLowerDetectionLimit()
    True

Check uncertainty when the result is exactly on a detection limit:

    >>> cu.setResult("21")
    >>> cu.isAboveUpperDetectionLimit()
    False

    >>> cu.setUncertainty("0.5")
    >>> cu.getUncertainty()
    '0.5'

    >>> cu.setResult("0")
    >>> cu.isBelowLowerDetectionLimit()
    False

    >>> cu.setUncertainty("0.001")
    >>> cu.getUncertainty()
    '0.001'


Test uncertainty formatting
...........................

The uncertainty is formatted in the analysis view according to the precision.

Import the required function:

    >>> from bika.lims.utils.analysis import format_uncertainty

Setup uncertainty settings in the service:

    >>> uncertainties = [
    ...    {"intercept_min":  "0", "intercept_max":  "5", "errorvalue": "0.00015"},
    ...    {"intercept_min":  "5", "intercept_max": "10", "errorvalue": "1%"},
    ...    {"intercept_min": "10", "intercept_max": "20", "errorvalue": "5%"},
    ... ]

    >>> Au.setUncertainties(uncertainties)
    >>> Au.setAllowManualUncertainty(False)
    >>> Au.setPrecisionFromUncertainty(False)

Create a new sample:

    >>> sample = new_sample([Cu, Fe, Au])
    >>> au = get_analysis(sample, Au)

Since we have neither specified a precision in the analysis service, nor did we allow to
set the precision from uncertainty, we get a precision of 0:

    >>> au.setResult("1.4")
    >>> format_uncertainty(au)
    '0'

When we set the precision in the analysis, the uncertainty is formatted to this value:

XXX: Why is it not rounded to 0.0002?

    >>> au.setPrecision(4)
    >>> format_uncertainty(au)
    '0.0001'

    >>> au.setPrecision(5)
    >>> format_uncertainty(au)
    '0.00015'

    >>> au.setPrecision(6)
    >>> format_uncertainty(au)
    '0.00015'

When the user manually entered an uncertainty and overrides an uncertainty
range, we always show all digits:

    >>> au.setPrecision(None)
    >>> au.setAllowManualUncertainty(True)
    >>> au.setUncertainty("0.00000123")
    >>> format_uncertainty(au)
    '0.00000123'

The uncertainty can be also defined as a percentage of the result and is then
calculated for the given range automaticall (if no manual uncertainty was set).

Test the range 5-10 with an unertainty value of 1% of the result:

    >>> au.setUncertainty(None)
    >>> au.setResult(7)
    >>> au.getUncertainty()
    '0.07'

Test the range 10-20 with an unertainty value of 5% of the result:

    >>> au.setResult(15)
    >>> au.getUncertainty()
    '0.75'

If the uncertainty value is not above 0, no formatted uncertainty is returned.
The use of `0` as an uncertainty value is useful for when the result is between
the detection limit and the quantification limit. In such case, uncertainty
mustn't be displayed. Likewise, there might be other scenarios in which the
user do not want to display uncertainty for a given result range:

    >>> uncertainties = [
    ...    {"intercept_min":  "0.2", "intercept_max":  "100000", "errorvalue": "5.3%"},
    ...    {"intercept_min":  "0.08", "intercept_max": "0.19", "errorvalue": "0"},
    ... ]

    >>> au.setUncertainties(uncertainties)
    >>> au.setResult(0.3)
    >>> au.getUncertainty()
    '0.0159'
    >>> format_uncertainty(au)
    '0.02'

    >>> au.setResult(0.05)
    >>> au.getUncertainty() is None
    True
    >>> format_uncertainty(au)
    ''

    >>> au.setResult(0.10)
    >>> au.getUncertainty()
    '0'
    >>> format_uncertainty(au)
    ''

Test exponential format
.......................

Create a new sample:

    >>> sample = new_sample([Cu, Fe, Au])
    >>> au = get_analysis(sample, Au)
    >>> au.setAllowManualUncertainty(True)
    >>> au.setPrecisionFromUncertainty(False)

Manually set the result and uncertainty:

    >>> au.setResult("1.000123e-5")
    >>> au.setUncertainty("0.002e-5")

We expect manual uncertainties in full precision:

    >>> au.getUncertainty()
    '0.002e-5'

    >>> format_uncertainty(au, sciformat=1)
    '2e-08'

    >>> format_uncertainty(au, sciformat=2)
    '2x10^-8'

    >>> format_uncertainty(au, sciformat=3)
    '2x10<sup>-8</sup>'

    >>> format_uncertainty(au, sciformat=4)
    '2\xc2\xb710^-8'

    >>> format_uncertainty(au, sciformat=5)
    '2\xc2\xb710<sup>-8</sup>'


Test floating point arithmetic
..............................

Currently, we convert all values internally to `float` values.
These values loose precision as more digits in the fractional part are:

    >>> 0.0005
    0.0005

    >>> 0.00005
    5e-05

    >>> 1.00005
    1.00005


    >>> 1.00000000000000000005
    1.0

This means, that storing values as `float` values would loose precision ins ome
cases and no longer match the value entered by the user.

Therefore, we store the uncertainty as string values:

    >>> sample = new_sample([Cu, Fe, Au])
    >>> au = get_analysis(sample, Au)

    >>> au.setAllowManualUncertainty(True)
    >>> au.setResult(10)

Python returns the exponential notation for this value (see above):

    >>> au.setUncertainty("0.00005")
    >>> au.getUncertainty()
    '0.00005'

Define it as an uncertainty as percentage of the result:

    >>> uncertainties = [
    ...    {"intercept_min": "0", "intercept_max": "10", "errorvalue": "0.00001%"},
    ... ]

    >>> au.setUncertainties(uncertainties)
    >>> au.setUncertainty(None)
    >>> au.getUncertainty()
    '0.000001'

    >>> format_uncertainty(au)
    '0.000001'


    >>> uncertainties = [
    ...    {"intercept_min": "0", "intercept_max": "10", "errorvalue": "0.00000000000000000001%"},
    ... ]

    >>> au.setUncertainties(uncertainties)

    >>> au.getUncertainty()
    '0.000000000000000000001'

Because it exceeded the Exponential format precision, it is returned with the scientific notation:

    >>> format_uncertainty(au)
    '1.0e-21'

Change to a higher precision threshold:

    >>> au.setExponentialFormatPrecision(30)
    >>> format_uncertainty(au)
    '0.000000000000000000001'
