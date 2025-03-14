Limits
------

It is possible to assign Limits of Detection and Quantification to services and
analyses. The way results are formatted and displayed for visualization and in
reports depend on these limits.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t Limits


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

    >>> def new_sample(services):
    ...     values = {
    ...         'Client': client,
    ...         'Contact': contact,
    ...         'DateSampled': date_now,
    ...         'SampleType': sampletype
    ...     }
    ...     sample = create_analysisrequest(client, request, values, services)
    ...     transitioned = do_action_for(sample, "receive")
    ...     return sample

    >>> def get_analysis(sample, service):
    ...     service_uid = api.get_uid(service)
    ...     for analysis in sample.getAnalyses(full_objects=True):
    ...         if analysis.getServiceUID() == service_uid:
    ...             return analysis
    ...     return None

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bika_setup = portal.bika_setup
    >>> date_now = DateTime().strftime("%Y-%m-%d")

Create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bika_setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bika_setup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Category=category)


Test detection range
....................

We allow users to input the Lower Limit of Detection (LLOD) and the Upper
Limit of Detection (ULOD), which together define the range within which the
concentration of the analyte can be reliably **detected**:

    >>> Cu.setLowerDetectionLimit("10")
    >>> Cu.setUpperDetectionLimit("20")

Create a sample:

    >>> sample = new_sample([Cu])
    >>> cu = get_analysis(sample, Cu)

The result is formatted as `< LLOD` when below the Lower Limit of Detection
(LLOD):

    >>> cu.setResult(5)
    >>> cu.isBelowLowerDetectionLimit()
    True
    >>> cu.isAboveUpperDetectionLimit()
    False
    >>> cu.getFormattedResult()
    '&lt; 10'
    >>> cu.getFormattedResult(html=False)
    '< 10'

The result is not formatted when equals to LLOD:

    >>> cu.setResult(10)
    >>> cu.isBelowLowerDetectionLimit()
    False
    >>> cu.isAboveUpperDetectionLimit()
    False
    >>> cu.getFormattedResult()
    '10'

The result is not formatted when equals to ULOD:

    >>> cu.setResult(20)
    >>> cu.isBelowLowerDetectionLimit()
    False
    >>> cu.isAboveUpperDetectionLimit()
    False
    >>> cu.getFormattedResult()
    '20'

The result is formatted as `> ULOD` when above the Upper Limit of Detection
(ULOD):

    >>> cu.setResult(25)
    >>> cu.isBelowLowerDetectionLimit()
    False
    >>> cu.isAboveUpperDetectionLimit()
    True
    >>> cu.getFormattedResult()
    '&gt; 20'
    >>> cu.getFormattedResult(html=False)
    '> 20'


Test quantifiable range
.......................

We allow users to input the Lower Limit of Quantification (LLOQ) and the Upper
Limit of Quantification (ULOQ), which together define the range within which
the concentration of the analyte can be reliably **quantified**.

We can set the same range for quantifiable as for detection:

    >>> Cu.setLowerDetectionLimit("10")
    >>> Cu.setUpperDetectionLimit("20")
    >>> Cu.setLowerLimitOfQuantification("10")
    >>> Cu.setUpperLimitOfQuantification("20")

Create a sample:

    >>> sample = new_sample([Cu])
    >>> cu = get_analysis(sample, Cu)

The result is formatted as `< LLOQ` when below the Lower Limit of
Quantification (LLOQ):

    >>> cu.setResult(5)
    >>> cu.isBelowLowerDetectionLimit()
    True
    >>> cu.isAboveUpperDetectionLimit()
    False
    >>> cu.isOutsideTheQuantifiableRange()
    True
    >>> cu.getFormattedResult()
    '&lt; 10'
    >>> cu.getFormattedResult(html=False)
    '< 10'

The result is not formatted when equals to LLOQ:

    >>> cu.setResult(10)
    >>> cu.isBelowLowerDetectionLimit()
    False
    >>> cu.isAboveUpperDetectionLimit()
    False
    >>> cu.isOutsideTheQuantifiableRange()
    False
    >>> cu.getFormattedResult()
    '10'

The result is not formatted when equals to ULOQ:

    >>> cu.setResult(20)
    >>> cu.isBelowLowerDetectionLimit()
    False
    >>> cu.isAboveUpperDetectionLimit()
    False
    >>> cu.isOutsideTheQuantifiableRange()
    False
    >>> cu.getFormattedResult()
    '20'

The result is formatted as `> ULOQ` when above the Upper Limit of
Quantification (ULOQ):

    >>> cu.setResult(25)
    >>> cu.isBelowLowerDetectionLimit()
    False
    >>> cu.isAboveUpperDetectionLimit()
    True
    >>> cu.isOutsideTheQuantifiableRange()
    True
    >>> cu.getFormattedResult()
    '&gt; 20'
    >>> cu.getFormattedResult(html=False)
    '> 20'


Test quantifiable and detection range altogether
................................................

Set different ranges for quantifiable and detection. Note that the
quantifiable range is always nested within the detection range:.

    >>> Cu.setLowerDetectionLimit("5")
    >>> Cu.setUpperDetectionLimit("25")
    >>> Cu.setLowerLimitOfQuantification("10")
    >>> Cu.setUpperLimitOfQuantification("20")

Create a sample:

    >>> sample = new_sample([Cu])
    >>> cu = get_analysis(sample, Cu)

The result is formatted as `Not detected` when below the LLOD:

    >>> cu.setResult(2)
    >>> cu.isBelowLowerDetectionLimit()
    True
    >>> cu.isAboveUpperDetectionLimit()
    False
    >>> cu.isOutsideTheQuantifiableRange()
    True
    >>> cu.getFormattedResult()
    'Not detected'

The result is formatted as `Detected but < LLOQ` when equal to LLOD:

    >>> cu.setResult(5)
    >>> cu.isBelowLowerDetectionLimit()
    False
    >>> cu.isAboveUpperDetectionLimit()
    False
    >>> cu.isOutsideTheQuantifiableRange()
    True
    >>> cu.getFormattedResult()
    'Detected but &lt; 10'
    >>> cu.getFormattedResult(html=False)
    'Detected but < 10'

Result is formatted as `Detected but < LLOQ` when above LLOD but below LLOQ:

    >>> cu.setResult(5)
    >>> cu.isBelowLowerDetectionLimit()
    False
    >>> cu.isAboveUpperDetectionLimit()
    False
    >>> cu.isOutsideTheQuantifiableRange()
    True
    >>> cu.getFormattedResult()
    'Detected but &lt; 10'
    >>> cu.getFormattedResult(html=False)
    'Detected but < 10'

The result is not formatted when equal to LLOQ:

    >>> cu.setResult(10)
    >>> cu.isBelowLowerDetectionLimit()
    False
    >>> cu.isAboveUpperDetectionLimit()
    False
    >>> cu.isOutsideTheQuantifiableRange()
    False
    >>> cu.getFormattedResult()
    '10'

The result is not formatted when within quantifiable range:

    >>> cu.setResult(15)
    >>> cu.isBelowLowerDetectionLimit()
    False
    >>> cu.isAboveUpperDetectionLimit()
    False
    >>> cu.isOutsideTheQuantifiableRange()
    False
    >>> cu.getFormattedResult()
    '15'

The result is not formatted when equal to ULOQ:

    >>> cu.setResult(20)
    >>> cu.isBelowLowerDetectionLimit()
    False
    >>> cu.isAboveUpperDetectionLimit()
    False
    >>> cu.isOutsideTheQuantifiableRange()
    False
    >>> cu.getFormattedResult()
    '20'

The result is formatted as `> ULOQ` when above ULOQ but below ULOD:

    >>> cu.setResult(22)
    >>> cu.isBelowLowerDetectionLimit()
    False
    >>> cu.isAboveUpperDetectionLimit()
    False
    >>> cu.isOutsideTheQuantifiableRange()
    True
    >>> cu.getFormattedResult()
    '&gt; 20'
    >>> cu.getFormattedResult(html=False)
    '> 20'

The result is formatted as `> ULOQ` when equals ULOD:

    >>> cu.setResult(25)
    >>> cu.isBelowLowerDetectionLimit()
    False
    >>> cu.isAboveUpperDetectionLimit()
    False
    >>> cu.isOutsideTheQuantifiableRange()
    True
    >>> cu.getFormattedResult()
    '&gt; 20'
    >>> cu.getFormattedResult(html=False)
    '> 20'

The result is formatted as `> ULOQ` when above ULOD:

    >>> cu.setResult(30)
    >>> cu.isBelowLowerDetectionLimit()
    False
    >>> cu.isAboveUpperDetectionLimit()
    True
    >>> cu.isOutsideTheQuantifiableRange()
    True
    >>> cu.getFormattedResult()
    '&gt; 20'
    >>> cu.getFormattedResult(html=False)
    '> 20'
