SENAITE Setup
-------------

The SENAITE Setup folder is a Dexterity container which holds global configuration settings.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t SenaiteSetup


Test Setup
..........

Needed Imports:

    >>> from operator import methodcaller
    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from DateTime import DateTime
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.analysisrequest import create_partition
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from plone.app.testing import setRoles

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def new_sample(services, client, contact, sample_type, date_sampled=None):
    ...     values = {
    ...         'Client': api.get_uid(client),
    ...         'Contact': api.get_uid(contact),
    ...         'DateSampled': date_sampled or DateTime().strftime("%Y-%m-%d"),
    ...         'SampleType': api.get_uid(sample_type),
    ...     }
    ...     service_uids = map(api.get_uid, services)
    ...     sample = create_analysisrequest(client, request, values, service_uids)
    ...     return sample


Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = api.get_bika_setup()

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())


Senaite Setup Container
.......................

Fetch the object with the API:

    >>> senaite_setup = api.get_senaite_setup()
    >>> senaite_setup
    <Setup at /plone/setup>

The container should follow the `senaite_setup_workflow`:

    >>> api.get_workflows_for(senaite_setup)
    ('senaite_setup_workflow',)


Security Fields
...............

Auto Log Off:

    >>> senaite_setup.setAutoLogOff(30)
    >>> senaite_setup.getAutoLogOff()
    30

    >>> bikasetup.getAutoLogOff() == senaite_setup.getAutoLogOff()
    True

    >>> bikasetup.setAutoLogOff(60)
    >>> bikasetup.getAutoLogOff()
    60

    >>> bikasetup.getAutoLogOff() == senaite_setup.getAutoLogOff()
    True

Restrict Worksheet Users Access:

    >>> senaite_setup.setRestrictWorksheetUsersAccess(True)
    >>> senaite_setup.getRestrictWorksheetUsersAccess()
    True

    >>> bikasetup.getRestrictWorksheetUsersAccess() == senaite_setup.getRestrictWorksheetUsersAccess()
    True

    >>> bikasetup.setRestrictWorksheetUsersAccess(False)
    >>> bikasetup.getRestrictWorksheetUsersAccess()
    False

    >>> bikasetup.getRestrictWorksheetUsersAccess() == senaite_setup.getRestrictWorksheetUsersAccess()
    True

Allow To Submit Not Assigned:

    >>> senaite_setup.setAllowToSubmitNotAssigned(True)
    >>> senaite_setup.getAllowToSubmitNotAssigned()
    True

    >>> bikasetup.getAllowToSubmitNotAssigned() == senaite_setup.getAllowToSubmitNotAssigned()
    True

    >>> bikasetup.setAllowToSubmitNotAssigned(False)
    >>> bikasetup.getAllowToSubmitNotAssigned()
    False

    >>> bikasetup.getAllowToSubmitNotAssigned() == senaite_setup.getAllowToSubmitNotAssigned()
    True

Restrict Worksheet Management:

    >>> senaite_setup.setRestrictWorksheetManagement(True)
    >>> senaite_setup.getRestrictWorksheetManagement()
    True

    >>> bikasetup.getRestrictWorksheetManagement() == senaite_setup.getRestrictWorksheetManagement()
    True

    >>> bikasetup.setRestrictWorksheetManagement(False)
    >>> bikasetup.getRestrictWorksheetManagement()
    False

    >>> bikasetup.getRestrictWorksheetManagement() == senaite_setup.getRestrictWorksheetManagement()
    True

Enable Global Auditlog:

    >>> senaite_setup.setEnableGlobalAuditlog(True)
    >>> senaite_setup.getEnableGlobalAuditlog()
    True

    >>> bikasetup.getEnableGlobalAuditlog() == senaite_setup.getEnableGlobalAuditlog()
    True

    >>> bikasetup.setEnableGlobalAuditlog(False)
    >>> bikasetup.getEnableGlobalAuditlog()
    False

    >>> bikasetup.getEnableGlobalAuditlog() == senaite_setup.getEnableGlobalAuditlog()
    True


Accounting Fields
.................

Show Prices:

    >>> senaite_setup.setShowPrices(True)
    >>> senaite_setup.getShowPrices()
    True

    >>> bikasetup.getShowPrices() == senaite_setup.getShowPrices()
    True

    >>> bikasetup.setShowPrices(False)
    >>> bikasetup.getShowPrices()
    False

    >>> bikasetup.getShowPrices() == senaite_setup.getShowPrices()
    True

Currency:

    >>> senaite_setup.setCurrency(u"EUR")
    >>> senaite_setup.getCurrency()
    u'EUR'

    >>> bikasetup.getCurrency() == senaite_setup.getCurrency()
    True

    >>> bikasetup.setCurrency(u"USD")
    >>> bikasetup.getCurrency()
    u'USD'

    >>> bikasetup.getCurrency() == senaite_setup.getCurrency()
    True

Default Country:

    >>> senaite_setup.setDefaultCountry(u"de")
    >>> senaite_setup.getDefaultCountry()
    u'de'

    >>> bikasetup.getDefaultCountry() == senaite_setup.getDefaultCountry()
    True

    >>> bikasetup.setDefaultCountry(u"us")
    >>> bikasetup.getDefaultCountry()
    u'us'

    >>> bikasetup.getDefaultCountry() == senaite_setup.getDefaultCountry()
    True

Member Discount:

    >>> senaite_setup.setMemberDiscount(u"10.0")
    >>> senaite_setup.getMemberDiscount()
    u'10.0'

    >>> bikasetup.getMemberDiscount() == senaite_setup.getMemberDiscount()
    True

    >>> bikasetup.setMemberDiscount(u"15.5")
    >>> bikasetup.getMemberDiscount()
    u'15.5'

    >>> bikasetup.getMemberDiscount() == senaite_setup.getMemberDiscount()
    True

VAT:

    >>> senaite_setup.setVAT(u"19.0")
    >>> senaite_setup.getVAT()
    u'19.0'

    >>> bikasetup.getVAT() == senaite_setup.getVAT()
    True

    >>> bikasetup.setVAT(u"20.0")
    >>> bikasetup.getVAT()
    u'20.0'

    >>> bikasetup.getVAT() == senaite_setup.getVAT()
    True


Results Reports Fields
......................

Decimal Mark:

    >>> senaite_setup.setDecimalMark(u".")
    >>> senaite_setup.getDecimalMark()
    u'.'

    >>> bikasetup.getDecimalMark() == senaite_setup.getDecimalMark()
    True

    >>> bikasetup.setDecimalMark(u",")
    >>> bikasetup.getDecimalMark()
    u','

    >>> bikasetup.getDecimalMark() == senaite_setup.getDecimalMark()
    True

Scientific Notation Report:

    >>> senaite_setup.setScientificNotationReport(2)
    >>> senaite_setup.getScientificNotationReport()
    2

    >>> bikasetup.getScientificNotationReport() == senaite_setup.getScientificNotationReport()
    True

    >>> bikasetup.setScientificNotationReport(4)
    >>> bikasetup.getScientificNotationReport()
    4

    >>> bikasetup.getScientificNotationReport() == senaite_setup.getScientificNotationReport()
    True

Minimum Results:

    >>> senaite_setup.setMinimumResults(5)
    >>> senaite_setup.getMinimumResults()
    5

    >>> bikasetup.getMinimumResults() == senaite_setup.getMinimumResults()
    True

    >>> bikasetup.setMinimumResults(10)
    >>> bikasetup.getMinimumResults()
    10

    >>> bikasetup.getMinimumResults() == senaite_setup.getMinimumResults()
    True


Analyses Fields
...............

Categorise Analysis Services:

    >>> senaite_setup.setCategoriseAnalysisServices(True)
    >>> senaite_setup.getCategoriseAnalysisServices()
    True

    >>> bikasetup.getCategoriseAnalysisServices() == senaite_setup.getCategoriseAnalysisServices()
    True

    >>> bikasetup.setCategoriseAnalysisServices(False)
    >>> bikasetup.getCategoriseAnalysisServices()
    False

    >>> bikasetup.getCategoriseAnalysisServices() == senaite_setup.getCategoriseAnalysisServices()
    True

Categorize Sample Analyses:

    >>> senaite_setup.setCategorizeSampleAnalyses(True)
    >>> senaite_setup.getCategorizeSampleAnalyses()
    True

    >>> bikasetup.getCategorizeSampleAnalyses() == senaite_setup.getCategorizeSampleAnalyses()
    True

    >>> bikasetup.setCategorizeSampleAnalyses(False)
    >>> bikasetup.getCategorizeSampleAnalyses()
    False

    >>> bikasetup.getCategorizeSampleAnalyses() == senaite_setup.getCategorizeSampleAnalyses()
    True

Sample Analyses Required:

    >>> senaite_setup.setSampleAnalysesRequired(True)
    >>> senaite_setup.getSampleAnalysesRequired()
    True

    >>> bikasetup.getSampleAnalysesRequired() == senaite_setup.getSampleAnalysesRequired()
    True

    >>> bikasetup.setSampleAnalysesRequired(False)
    >>> bikasetup.getSampleAnalysesRequired()
    False

    >>> bikasetup.getSampleAnalysesRequired() == senaite_setup.getSampleAnalysesRequired()
    True

Allow Manual Result Capture Date:

    >>> senaite_setup.setAllowManualResultCaptureDate(True)
    >>> senaite_setup.getAllowManualResultCaptureDate()
    True

    >>> bikasetup.getAllowManualResultCaptureDate() == senaite_setup.getAllowManualResultCaptureDate()
    True

    >>> bikasetup.setAllowManualResultCaptureDate(False)
    >>> bikasetup.getAllowManualResultCaptureDate()
    False

    >>> bikasetup.getAllowManualResultCaptureDate() == senaite_setup.getAllowManualResultCaptureDate()
    True

Enable AR Specs:

    >>> senaite_setup.setEnableARSpecs(True)
    >>> senaite_setup.getEnableARSpecs()
    True

    >>> bikasetup.getEnableARSpecs() == senaite_setup.getEnableARSpecs()
    True

    >>> bikasetup.setEnableARSpecs(False)
    >>> bikasetup.getEnableARSpecs()
    False

    >>> bikasetup.getEnableARSpecs() == senaite_setup.getEnableARSpecs()
    True

Exponential Format Threshold:

    >>> senaite_setup.setExponentialFormatThreshold(7)
    >>> senaite_setup.getExponentialFormatThreshold()
    7

    >>> bikasetup.getExponentialFormatThreshold() == senaite_setup.getExponentialFormatThreshold()
    True

    >>> bikasetup.setExponentialFormatThreshold(9)
    >>> bikasetup.getExponentialFormatThreshold()
    9

    >>> bikasetup.getExponentialFormatThreshold() == senaite_setup.getExponentialFormatThreshold()
    True

Immediate Results Entry:

    >>> senaite_setup.setImmediateResultsEntry(True)
    >>> senaite_setup.getImmediateResultsEntry()
    True

    >>> bikasetup.getImmediateResultsEntry() == senaite_setup.getImmediateResultsEntry()
    True

    >>> bikasetup.setImmediateResultsEntry(False)
    >>> bikasetup.getImmediateResultsEntry()
    False

    >>> bikasetup.getImmediateResultsEntry() == senaite_setup.getImmediateResultsEntry()
    True

Enable Analysis Remarks:

    >>> senaite_setup.setEnableAnalysisRemarks(True)
    >>> senaite_setup.getEnableAnalysisRemarks()
    True

    >>> bikasetup.getEnableAnalysisRemarks() == senaite_setup.getEnableAnalysisRemarks()
    True

    >>> bikasetup.setEnableAnalysisRemarks(False)
    >>> bikasetup.getEnableAnalysisRemarks()
    False

    >>> bikasetup.getEnableAnalysisRemarks() == senaite_setup.getEnableAnalysisRemarks()
    True

Auto Verify Samples:

    >>> senaite_setup.setAutoVerifySamples(True)
    >>> senaite_setup.getAutoVerifySamples()
    True

    >>> bikasetup.getAutoVerifySamples() == senaite_setup.getAutoVerifySamples()
    True

    >>> bikasetup.setAutoVerifySamples(False)
    >>> bikasetup.getAutoVerifySamples()
    False

    >>> bikasetup.getAutoVerifySamples() == senaite_setup.getAutoVerifySamples()
    True

Self Verification Enabled:

    >>> senaite_setup.setSelfVerificationEnabled(True)
    >>> senaite_setup.getSelfVerificationEnabled()
    True

    >>> bikasetup.getSelfVerificationEnabled() == senaite_setup.getSelfVerificationEnabled()
    True

    >>> bikasetup.setSelfVerificationEnabled(False)
    >>> bikasetup.getSelfVerificationEnabled()
    False

    >>> bikasetup.getSelfVerificationEnabled() == senaite_setup.getSelfVerificationEnabled()
    True

Number Of Required Verifications:

    >>> senaite_setup.setNumberOfRequiredVerifications(2)
    >>> senaite_setup.getNumberOfRequiredVerifications()
    2

    >>> bikasetup.getNumberOfRequiredVerifications() == senaite_setup.getNumberOfRequiredVerifications()
    True

    >>> bikasetup.setNumberOfRequiredVerifications(3)
    >>> bikasetup.getNumberOfRequiredVerifications()
    3

    >>> bikasetup.getNumberOfRequiredVerifications() == senaite_setup.getNumberOfRequiredVerifications()
    True

Type Of Multi Verification:

    >>> senaite_setup.setTypeOfmultiVerification(u"self_multi_enabled")
    >>> senaite_setup.getTypeOfmultiVerification()
    u'self_multi_enabled'

    >>> bikasetup.getTypeOfmultiVerification() == senaite_setup.getTypeOfmultiVerification()
    True

    >>> bikasetup.setTypeOfmultiVerification(u"self_multi_disabled")
    >>> bikasetup.getTypeOfmultiVerification()
    u'self_multi_disabled'

    >>> bikasetup.getTypeOfmultiVerification() == senaite_setup.getTypeOfmultiVerification()
    True

Results Decimal Mark:

    >>> senaite_setup.setResultsDecimalMark(u".")
    >>> senaite_setup.getResultsDecimalMark()
    u'.'

    >>> bikasetup.getResultsDecimalMark() == senaite_setup.getResultsDecimalMark()
    True

    >>> bikasetup.setResultsDecimalMark(u",")
    >>> bikasetup.getResultsDecimalMark()
    u','

    >>> bikasetup.getResultsDecimalMark() == senaite_setup.getResultsDecimalMark()
    True

Scientific Notation Results:

    >>> senaite_setup.setScientificNotationResults(5)
    >>> senaite_setup.getScientificNotationResults()
    5

    >>> bikasetup.getScientificNotationResults() == senaite_setup.getScientificNotationResults()
    True

    >>> bikasetup.setScientificNotationResults(6)
    >>> bikasetup.getScientificNotationResults()
    6

    >>> bikasetup.getScientificNotationResults() == senaite_setup.getScientificNotationResults()
    True

Rejection Reasons:

    >>> test_reasons = [u"Sample damaged", u"Insufficient volume"]
    >>> senaite_setup.setEnableRejectionWorkflow(True)
    >>> senaite_setup.setRejectionReasons(test_reasons)
    >>> senaite_setup.getRejectionReasons()
    [u'Sample damaged', u'Insufficient volume']

    >>> senaite_setup.getEnableRejectionWorkflow()
    True

    >>> bikasetup.getRejectionReasonsItems()
    [u'Sample damaged', u'Insufficient volume']

    >>> bikasetup.setRejectionReasons([u"Test reason 1", u"Test reason 2"])
    >>> bikasetup.getRejectionReasonsItems()
    [u'Test reason 1', u'Test reason 2']

    >>> senaite_setup.getRejectionReasons()
    [u'Test reason 1', u'Test reason 2']

Default Number Of ARs To Add:

    >>> senaite_setup.setDefaultNumberOfARsToAdd(5)
    >>> senaite_setup.getDefaultNumberOfARsToAdd()
    5

    >>> bikasetup.getDefaultNumberOfARsToAdd() == senaite_setup.getDefaultNumberOfARsToAdd()
    True

    >>> bikasetup.setDefaultNumberOfARsToAdd(10)
    >>> bikasetup.getDefaultNumberOfARsToAdd()
    10

    >>> bikasetup.getDefaultNumberOfARsToAdd() == senaite_setup.getDefaultNumberOfARsToAdd()
    True

Max Number Of Samples Add:

    >>> senaite_setup.setMaxNumberOfSamplesAdd(20)
    >>> senaite_setup.getMaxNumberOfSamplesAdd()
    20

    >>> bikasetup.getMaxNumberOfSamplesAdd() == senaite_setup.getMaxNumberOfSamplesAdd()
    True

    >>> bikasetup.setMaxNumberOfSamplesAdd(30)
    >>> bikasetup.getMaxNumberOfSamplesAdd()
    30

    >>> bikasetup.getMaxNumberOfSamplesAdd() == senaite_setup.getMaxNumberOfSamplesAdd()
    True


Appearance Fields
.................

Worksheet Layout:

    >>> senaite_setup.setWorksheetLayout(u"classic")
    >>> senaite_setup.getWorksheetLayout()
    u'classic'

    >>> bikasetup.getWorksheetLayout() == senaite_setup.getWorksheetLayout()
    True

    >>> bikasetup.setWorksheetLayout(u"modern")
    >>> bikasetup.getWorksheetLayout()
    u'modern'

    >>> bikasetup.getWorksheetLayout() == senaite_setup.getWorksheetLayout()
    True

Show Partitions:

    >>> senaite_setup.setShowPartitions(True)
    >>> senaite_setup.getShowPartitions()
    True

    >>> bikasetup.getShowPartitions() == senaite_setup.getShowPartitions()
    True

    >>> bikasetup.setShowPartitions(False)
    >>> bikasetup.getShowPartitions()
    False

    >>> bikasetup.getShowPartitions() == senaite_setup.getShowPartitions()
    True

Show Lab Name In Login:

    >>> senaite_setup.setShowLabNameInLogin(True)
    >>> senaite_setup.getShowLabNameInLogin()
    True

    >>> bikasetup.getShowLabNameInLogin() == senaite_setup.getShowLabNameInLogin()
    True

    >>> bikasetup.setShowLabNameInLogin(False)
    >>> bikasetup.getShowLabNameInLogin()
    False

    >>> bikasetup.getShowLabNameInLogin() == senaite_setup.getShowLabNameInLogin()
    True


Sampling Fields
...............

Printing Workflow Enabled:

    >>> senaite_setup.setPrintingWorkflowEnabled(True)
    >>> senaite_setup.getPrintingWorkflowEnabled()
    True

    >>> bikasetup.getPrintingWorkflowEnabled() == senaite_setup.getPrintingWorkflowEnabled()
    True

    >>> bikasetup.setPrintingWorkflowEnabled(False)
    >>> bikasetup.getPrintingWorkflowEnabled()
    False

    >>> bikasetup.getPrintingWorkflowEnabled() == senaite_setup.getPrintingWorkflowEnabled()
    True

Sampling Workflow Enabled:

    >>> senaite_setup.setSamplingWorkflowEnabled(True)
    >>> senaite_setup.getSamplingWorkflowEnabled()
    True

    >>> bikasetup.getSamplingWorkflowEnabled() == senaite_setup.getSamplingWorkflowEnabled()
    True

    >>> bikasetup.setSamplingWorkflowEnabled(False)
    >>> bikasetup.getSamplingWorkflowEnabled()
    False

    >>> bikasetup.getSamplingWorkflowEnabled() == senaite_setup.getSamplingWorkflowEnabled()
    True

Schedule Sampling Enabled:

    >>> senaite_setup.setScheduleSamplingEnabled(True)
    >>> senaite_setup.getScheduleSamplingEnabled()
    True

    >>> bikasetup.getScheduleSamplingEnabled() == senaite_setup.getScheduleSamplingEnabled()
    True

    >>> bikasetup.setScheduleSamplingEnabled(False)
    >>> bikasetup.getScheduleSamplingEnabled()
    False

    >>> bikasetup.getScheduleSamplingEnabled() == senaite_setup.getScheduleSamplingEnabled()
    True

Date Sampled Required:

    >>> senaite_setup.setDateSampledRequired(True)
    >>> senaite_setup.getDateSampledRequired()
    True

    >>> bikasetup.getDateSampledRequired() == senaite_setup.getDateSampledRequired()
    True

    >>> bikasetup.setDateSampledRequired(False)
    >>> bikasetup.getDateSampledRequired()
    False

    >>> bikasetup.getDateSampledRequired() == senaite_setup.getDateSampledRequired()
    True

Autoreceive Samples:

    >>> senaite_setup.setAutoreceiveSamples(True)
    >>> senaite_setup.getAutoreceiveSamples()
    True

    >>> bikasetup.getAutoreceiveSamples() == senaite_setup.getAutoreceiveSamples()
    True

    >>> bikasetup.setAutoreceiveSamples(False)
    >>> bikasetup.getAutoreceiveSamples()
    False

    >>> bikasetup.getAutoreceiveSamples() == senaite_setup.getAutoreceiveSamples()
    True

Sample Preservation Enabled:

    >>> senaite_setup.setSamplePreservationEnabled(True)
    >>> senaite_setup.getSamplePreservationEnabled()
    True

    >>> bikasetup.getSamplePreservationEnabled() == senaite_setup.getSamplePreservationEnabled()
    True

    >>> bikasetup.setSamplePreservationEnabled(False)
    >>> bikasetup.getSamplePreservationEnabled()
    False

    >>> bikasetup.getSamplePreservationEnabled() == senaite_setup.getSamplePreservationEnabled()
    True

Workdays:

    >>> senaite_setup.setWorkdays([1, 2, 3, 4, 5])
    >>> senaite_setup.getWorkdays()
    [1, 2, 3, 4, 5]

    >>> bikasetup.getWorkdays() == senaite_setup.getWorkdays()
    True

    >>> bikasetup.setWorkdays([1, 2, 3, 4, 5, 6])
    >>> bikasetup.getWorkdays()
    [1, 2, 3, 4, 5, 6]

    >>> bikasetup.getWorkdays() == senaite_setup.getWorkdays()
    True

Default Turnaround Time:

    >>> from datetime import timedelta
    >>> tat = timedelta(days=5)
    >>> senaite_setup.setDefaultTurnaroundTime(tat)
    >>> senaite_setup.getDefaultTurnaroundTime()
    datetime.timedelta(5)

    >>> bikasetup_tat = bikasetup.getDefaultTurnaroundTime()
    >>> sorted(bikasetup_tat.items())
    [('days', 5), ('hours', 0), ('minutes', 0), ('seconds', 0)]

    >>> tat2_dict = {'days': 7, 'hours': 0, 'minutes': 0, 'seconds': 0}
    >>> bikasetup.setDefaultTurnaroundTime(tat2_dict)
    >>> sorted(bikasetup.getDefaultTurnaroundTime().items())
    [('days', 7), ('hours', 0), ('minutes', 0), ('seconds', 0)]

    >>> senaite_setup.getDefaultTurnaroundTime()
    datetime.timedelta(7)

Default Sample Lifetime:

    >>> lifetime = timedelta(days=30)
    >>> senaite_setup.setDefaultSampleLifetime(lifetime)
    >>> senaite_setup.getDefaultSampleLifetime()
    datetime.timedelta(30)

    >>> bikasetup_lifetime = bikasetup.getDefaultSampleLifetime()
    >>> sorted(bikasetup_lifetime.items())
    [('days', 30), ('hours', 0), ('minutes', 0), ('seconds', 0)]

    >>> lifetime2_dict = {'days': 60, 'hours': 0, 'minutes': 0, 'seconds': 0}
    >>> bikasetup.setDefaultSampleLifetime(lifetime2_dict)
    >>> sorted(bikasetup.getDefaultSampleLifetime().items())
    [('days', 60), ('hours', 0), ('minutes', 0), ('seconds', 0)]

    >>> senaite_setup.getDefaultSampleLifetime()
    datetime.timedelta(60)


Notifications Fields
....................

Email From Sample Publication:

    >>> senaite_setup.setEmailFromSamplePublication(u"noreply@lab.com")
    >>> senaite_setup.getEmailFromSamplePublication()
    u'noreply@lab.com'

    >>> bikasetup.getEmailFromSamplePublication() == senaite_setup.getEmailFromSamplePublication()
    True

    >>> bikasetup.setEmailFromSamplePublication(u"results@lab.com")
    >>> bikasetup.getEmailFromSamplePublication()
    u'results@lab.com'

    >>> bikasetup.getEmailFromSamplePublication() == senaite_setup.getEmailFromSamplePublication()
    True

Email Body Sample Publication:

Initially, the field is empty and should return the default value:

    >>> from senaite.core.content.senaitesetup import default_email_body_sample_publication
    >>> default_body = default_email_body_sample_publication(senaite_setup)
    >>> senaite_setup.getEmailBodySamplePublication() == default_body
    True

A new value can be set via the provided setter:

    >>> senaite_setup.setEmailBodySamplePublication(u"Your results are there!")
    >>> senaite_setup.getEmailBodySamplePublication()
    u'Your results are there!'

The old setup provides proxy fields to get/set the value:

    >>> bikasetup.getEmailBodySamplePublication() == senaite_setup.getEmailBodySamplePublication()
    True

    >>> bikasetup.setEmailBodySamplePublication(u"Changes done via old setup UI")
    >>> bikasetup.getEmailBodySamplePublication()
    u'Changes done via old setup UI'

    >>> bikasetup.getEmailBodySamplePublication() == senaite_setup.getEmailBodySamplePublication()
    True

Always CC Responsibles In Report Email:

    >>> senaite_setup.setAlwaysCCResponsiblesInReportEmail(True)
    >>> senaite_setup.getAlwaysCCResponsiblesInReportEmail()
    True

    >>> bikasetup.getAlwaysCCResponsiblesInReportEmail() == senaite_setup.getAlwaysCCResponsiblesInReportEmail()
    True

    >>> bikasetup.setAlwaysCCResponsiblesInReportEmail(False)
    >>> bikasetup.getAlwaysCCResponsiblesInReportEmail()
    False

    >>> bikasetup.getAlwaysCCResponsiblesInReportEmail() == senaite_setup.getAlwaysCCResponsiblesInReportEmail()
    True

Notify On Sample Rejection:

    >>> senaite_setup.setNotifyOnSampleRejection(True)
    >>> senaite_setup.getNotifyOnSampleRejection()
    True

    >>> bikasetup.getNotifyOnSampleRejection() == senaite_setup.getNotifyOnSampleRejection()
    True

    >>> bikasetup.setNotifyOnSampleRejection(False)
    >>> bikasetup.getNotifyOnSampleRejection()
    False

    >>> bikasetup.getNotifyOnSampleRejection() == senaite_setup.getNotifyOnSampleRejection()
    True

Email Body Sample Rejection:

    >>> senaite_setup.setEmailBodySampleRejection(u"Your sample was rejected")
    >>> senaite_setup.getEmailBodySampleRejection()
    u'Your sample was rejected'

    >>> bikasetup.getEmailBodySampleRejection() == senaite_setup.getEmailBodySampleRejection()
    True

    >>> bikasetup.setEmailBodySampleRejection(u"Sample rejected: {rejection_reasons}")
    >>> bikasetup.getEmailBodySampleRejection()
    u'Sample rejected: {rejection_reasons}'

    >>> bikasetup.getEmailBodySampleRejection() == senaite_setup.getEmailBodySampleRejection()
    True

Invalidation Reason Required:

    >>> senaite_setup.setInvalidationReasonRequired(True)
    >>> senaite_setup.getInvalidationReasonRequired()
    True

    >>> bikasetup.getInvalidationReasonRequired() == senaite_setup.getInvalidationReasonRequired()
    True

    >>> bikasetup.setInvalidationReasonRequired(False)
    >>> bikasetup.getInvalidationReasonRequired()
    False

    >>> bikasetup.getInvalidationReasonRequired() == senaite_setup.getInvalidationReasonRequired()
    True

Email Body Sample Invalidation:

    >>> senaite_setup.setEmailBodySampleInvalidation(u"Sample invalidated")
    >>> senaite_setup.getEmailBodySampleInvalidation()
    u'Sample invalidated'

    >>> bikasetup.getEmailBodySampleInvalidation() == senaite_setup.getEmailBodySampleInvalidation()
    True

    >>> bikasetup.setEmailBodySampleInvalidation(u"Your sample was invalidated")
    >>> bikasetup.getEmailBodySampleInvalidation()
    u'Your sample was invalidated'

    >>> bikasetup.getEmailBodySampleInvalidation() == senaite_setup.getEmailBodySampleInvalidation()
    True


RichTextValue Handling for Email Bodies
.........................................

The email body getters should properly handle RichTextValue objects and return
the transformed text content instead of the RichTextValue object itself.

First, let's import the necessary components:

    >>> from plone.app.textfield import RichText
    >>> from plone.app.textfield.value import RichTextValue
    >>> from plone.app.textfield import IRichTextValue

Test Email Body Sample Publication with RichTextValue:

When setting a simple string, it gets converted to a RichTextValue internally,
but the getter should return the transformed output:

    >>> senaite_setup.setEmailBodySamplePublication(u"<p>Results ready!</p>")
    >>> result = senaite_setup.getEmailBodySamplePublication()
    >>> isinstance(result, basestring)
    True
    >>> u"Results ready!" in result
    True

The result should not be a RichTextValue object:

    >>> IRichTextValue.providedBy(result)
    False

Test Email Body Sample Rejection with RichTextValue:

Setting a string value and verifying it returns text, not RichTextValue:

    >>> senaite_setup.setEmailBodySampleRejection(u"<p>Sample rejected!</p>")
    >>> result = senaite_setup.getEmailBodySampleRejection()
    >>> isinstance(result, basestring)
    True
    >>> u"Sample rejected!" in result
    True

The result should not be a RichTextValue object:

    >>> IRichTextValue.providedBy(result)
    False

Verify the same via bikasetup:

    >>> result = bikasetup.getEmailBodySampleRejection()
    >>> isinstance(result, basestring)
    True
    >>> IRichTextValue.providedBy(result)
    False

Test Email Body Sample Invalidation with RichTextValue:

Setting a string value and verifying it returns text, not RichTextValue:

    >>> senaite_setup.setEmailBodySampleInvalidation(u"<p>Sample invalidated!</p>")
    >>> result = senaite_setup.getEmailBodySampleInvalidation()
    >>> isinstance(result, basestring)
    True
    >>> u"Sample invalidated!" in result
    True

The result should not be a RichTextValue object:

    >>> IRichTextValue.providedBy(result)
    False

Verify the same via bikasetup:

    >>> result = bikasetup.getEmailBodySampleInvalidation()
    >>> isinstance(result, basestring)
    True
    >>> IRichTextValue.providedBy(result)
    False

Test with more complex HTML content:

    >>> complex_html = u"<p>Dear Client,</p><p>Your sample <strong>$sample_id</strong> has been rejected.</p><p>Reasons: $reasons</p>"
    >>> senaite_setup.setEmailBodySampleRejection(complex_html)
    >>> result = senaite_setup.getEmailBodySampleRejection()
    >>> isinstance(result, basestring)
    True
    >>> u"$sample_id" in result
    True
    >>> u"$reasons" in result
    True

Verify consistency between senaite_setup and bikasetup:

    >>> senaite_setup.getEmailBodySampleRejection() == bikasetup.getEmailBodySampleRejection()
    True

    >>> complex_html_inv = u"<p>Sample <em>$sample_link</em> invalidated.</p><p>Retest: $retest_link</p>"
    >>> senaite_setup.setEmailBodySampleInvalidation(complex_html_inv)
    >>> result = senaite_setup.getEmailBodySampleInvalidation()
    >>> isinstance(result, basestring)
    True
    >>> u"$sample_link" in result
    True
    >>> u"$retest_link" in result
    True

Verify consistency between senaite_setup and bikasetup:

    >>> senaite_setup.getEmailBodySampleInvalidation() == bikasetup.getEmailBodySampleInvalidation()
    True

Test with unicode characters (German umlauts and special characters):

Unicode content in rejection email body should work without errors:

    >>> unicode_rejection = u"<p>Ihre Probe wurde abgelehnt: <strong>Gründe</strong></p><ul><li>Unzureichendes Volumen</li><li>Beschädigte Probe</li></ul>"
    >>> senaite_setup.setEmailBodySampleRejection(unicode_rejection)
    >>> result = senaite_setup.getEmailBodySampleRejection()
    >>> isinstance(result, basestring)
    True
    >>> u"Gründe" in result or "Gr\\xfcnde" in result or "Gründe" in result
    True
    >>> u"Unzureichendes" in result
    True
    >>> u"Beschädigte" in result or "Besch\\xe4digte" in result or "Beschädigte" in result
    True

Unicode content in invalidation email body should work without errors:

    >>> unicode_invalidation = u"<p>Probe <em>$sample_link</em> ungültig gemacht.</p><p>Grund: Fehlerhafte Messwerte (Überprüfung erforderlich)</p>"
    >>> senaite_setup.setEmailBodySampleInvalidation(unicode_invalidation)
    >>> result = senaite_setup.getEmailBodySampleInvalidation()
    >>> isinstance(result, basestring)
    True
    >>> u"ungültig" in result or "ung\\xfcltig" in result or "ungültig" in result
    True
    >>> u"Überprüfung" in result or "\\xdcberpr\\xfcfung" in result or "Überprüfung" in result
    True

Test rejection reasons with unicode characters:

Set unicode rejection reasons via bikasetup to ensure proper syncing:

    >>> unicode_reasons = [u"Füllmenge nicht ausreichend", u"Behälter beschädigt", u"Temperatur zu hoch (>25°C)"]
    >>> bikasetup.setRejectionReasons(unicode_reasons)
    >>> reasons = bikasetup.getRejectionReasons()
    >>> len(reasons)
    3
    >>> u"Füllmenge nicht ausreichend" in reasons or u"F\\xfcllmenge nicht ausreichend" in str(reasons) or "Füllmenge nicht ausreichend" in str(reasons)
    True
    >>> u"Behälter beschädigt" in reasons or u"Beh\\xe4lter besch\\xe4digt" in str(reasons) or "Behälter beschädigt" in str(reasons)
    True

Verify that both bikasetup and senaite_setup return the same unicode values:

    >>> senaite_reasons = senaite_setup.getRejectionReasons()
    >>> len(senaite_reasons)
    3
    >>> u"Füllmenge nicht ausreichend" in senaite_reasons or u"F\\xfcllmenge nicht ausreichend" in str(senaite_reasons) or "Füllmenge nicht ausreichend" in str(senaite_reasons)
    True
    >>> bikasetup.getRejectionReasons() == senaite_setup.getRejectionReasons()
    True

Verify getRejectionReasonsItems (deprecated) still works:

    >>> bikasetup.getRejectionReasonsItems() == bikasetup.getRejectionReasons()
    True


Sticker Fields
..............

Auto Print Stickers:

    >>> senaite_setup.setAutoPrintStickers(u"register")
    >>> senaite_setup.getAutoPrintStickers()
    u'register'

    >>> bikasetup.getAutoPrintStickers() == senaite_setup.getAutoPrintStickers()
    True

    >>> bikasetup.setAutoPrintStickers(u"receive")
    >>> bikasetup.getAutoPrintStickers()
    u'receive'

    >>> bikasetup.getAutoPrintStickers() == senaite_setup.getAutoPrintStickers()
    True

Auto Sticker Template:

    >>> senaite_setup.setAutoStickerTemplate(u"Code_128_40x20mm")
    >>> senaite_setup.getAutoStickerTemplate()
    u'Code_128_40x20mm'

    >>> bikasetup.getAutoStickerTemplate() == senaite_setup.getAutoStickerTemplate()
    True

    >>> bikasetup.setAutoStickerTemplate(u"Code_39_40x20mm")
    >>> bikasetup.getAutoStickerTemplate()
    u'Code_39_40x20mm'

    >>> bikasetup.getAutoStickerTemplate() == senaite_setup.getAutoStickerTemplate()
    True

Small Sticker Template:

    >>> senaite_setup.setSmallStickerTemplate(u"Code_128_20x10mm")
    >>> senaite_setup.getSmallStickerTemplate()
    u'Code_128_20x10mm'

    >>> bikasetup.getSmallStickerTemplate() == senaite_setup.getSmallStickerTemplate()
    True

    >>> bikasetup.setSmallStickerTemplate(u"Code_39_20x10mm")
    >>> bikasetup.getSmallStickerTemplate()
    u'Code_39_20x10mm'

    >>> bikasetup.getSmallStickerTemplate() == senaite_setup.getSmallStickerTemplate()
    True

Large Sticker Template:

    >>> senaite_setup.setLargeStickerTemplate(u"Code_128_60x30mm")
    >>> senaite_setup.getLargeStickerTemplate()
    u'Code_128_60x30mm'

    >>> bikasetup.getLargeStickerTemplate() == senaite_setup.getLargeStickerTemplate()
    True

    >>> bikasetup.setLargeStickerTemplate(u"Code_39_60x30mm")
    >>> bikasetup.getLargeStickerTemplate()
    u'Code_39_60x30mm'

    >>> bikasetup.getLargeStickerTemplate() == senaite_setup.getLargeStickerTemplate()
    True

Default Number Of Copies:

    >>> senaite_setup.setDefaultNumberOfCopies(2)
    >>> senaite_setup.getDefaultNumberOfCopies()
    2

    >>> bikasetup.getDefaultNumberOfCopies() == senaite_setup.getDefaultNumberOfCopies()
    True

    >>> bikasetup.setDefaultNumberOfCopies(3)
    >>> bikasetup.getDefaultNumberOfCopies()
    3

    >>> bikasetup.getDefaultNumberOfCopies() == senaite_setup.getDefaultNumberOfCopies()
    True


ID Server Fields
................

ID Formatting:

    >>> test_formatting = [
    ...     {"portal_type": u"AnalysisRequest", "form": u"AR-{seq:04d}", "sequence_type": u"counter", "context": u"", "counter_type": u"", "counter_reference": u"", "prefix": u"AR", "split_length": 1},
    ...     {"portal_type": u"Sample", "form": u"S-{seq:04d}", "sequence_type": u"generated", "context": u"", "counter_type": u"", "counter_reference": u"", "prefix": u"S", "split_length": 1}
    ... ]
    >>> senaite_setup.setIDFormatting(test_formatting)
    >>> formatting = senaite_setup.getIDFormatting()
    >>> len(formatting)
    2

Note: In Python 2, getIDFormatting returns byte strings (not unicode) to prevent
UnicodeDecodeError when formatting IDs with UTF-8 encoded values:

    >>> formatting[0]["portal_type"]
    'AnalysisRequest'

    >>> formatting[0]["form"]
    'AR-{seq:04d}'

    >>> bikasetup_formatting = bikasetup.getIDFormatting()
    >>> len(bikasetup_formatting)
    2

    >>> bikasetup_formatting[0]["portal_type"] == formatting[0]["portal_type"]
    True

    >>> test_formatting2 = [
    ...     {"portal_type": u"Batch", "form": u"B-{seq:05d}", "sequence_type": u"counter", "context": u"", "counter_type": u"", "counter_reference": u"", "prefix": u"B", "split_length": 1}
    ... ]
    >>> bikasetup.setIDFormatting(test_formatting2)
    >>> formatting2 = bikasetup.getIDFormatting()
    >>> len(formatting2)
    1

    >>> formatting2[0]["portal_type"]
    'Batch'

    >>> senaite_formatting2 = senaite_setup.getIDFormatting()
    >>> len(senaite_formatting2)
    1

    >>> senaite_formatting2[0]["portal_type"] == formatting2[0]["portal_type"]
    True
