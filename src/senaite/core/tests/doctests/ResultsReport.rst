Results Report
--------------

The ResultsReport content type stores published reports with their PDF content,
metadata about the report format and template, send log for email tracking, and
recipient information. This is the Dexterity successor to the Archetypes-based
ARReport.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t ResultsReport


Test Setup
..........

Needed Imports:

    >>> import transaction
    >>> from DateTime import DateTime
    >>> from plone import api as ploneapi
    >>> from plone.namedfile.file import NamedBlobFile
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor
    >>> from senaite.core.catalog import REPORT_CATALOG
    >>> from senaite.core.api import dtime
    >>> from datetime import datetime

Functional Helpers:

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

    >>> def new_sample(client, contact, sampletype, services):
    ...     values = {
    ...         "Client": client.UID(),
    ...         "Contact": contact.UID(),
    ...         "DateSampled": date_now,
    ...         "SampleType": sampletype.UID()
    ...     }
    ...     service_uids = [s.UID() for s in services]
    ...     return create_analysisrequest(
    ...         client, request, values, service_uids)

Variables:

    >>> date_now = timestamp()
    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bika_setup = portal.bika_setup
    >>> sampletypes = setup.sampletypes
    >>> analysiscategories = setup.analysiscategories
    >>> bika_analysisservices = bika_setup.bika_analysisservices

Test user:

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager.

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])


LIMS Setup
..........

Create a Client with Contact:

    >>> clients = portal.clients
    >>> client = api.create(
    ...     clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(
    ...     client, "Contact", Firstname="Rita", Lastname="Mohale")

Create a SampleType:

    >>> sampletype = api.create(
    ...     sampletypes, "SampleType", title="Water", Prefix="W")

Create an AnalysisCategory:

    >>> category = api.create(
    ...     analysiscategories, "AnalysisCategory", title="Chemistry")

Create AnalysisServices:

    >>> service_ph = api.create(
    ...     bika_analysisservices,
    ...     "AnalysisService",
    ...     title="pH",
    ...     ShortTitle="pH",
    ...     Category=category,
    ...     Keyword="PH")
    >>> service_temp = api.create(
    ...     bika_analysisservices,
    ...     "AnalysisService",
    ...     title="Temperature",
    ...     ShortTitle="Temp",
    ...     Category=category,
    ...     Keyword="TEMP")


Create Sample
.............

Create an AnalysisRequest (Sample):

    >>> sample = new_sample(
    ...     client, contact, sampletype, [service_ph, service_temp])
    >>> sample
    <AnalysisRequest at /plone/clients/client-...>

    >>> sample.getId()
    'W-0001'


Creating a ResultsReport
.........................

ResultsReport objects are typically created by senaite.impress when publishing
reports. They are stored as children of the primary AnalysisRequest:

    >>> report = api.create(sample, "ResultsReport")
    >>> report
    <ResultsReport at /plone/clients/client-.../...>

The report should be catalogued in the report catalog:

    >>> catalog = api.get_tool(REPORT_CATALOG)
    >>> brains = catalog({"portal_type": "ResultsReport"})
    >>> len(brains) >= 1
    True


Setting Primary Sample
......................

The primary sample is a required field and links the report to an
AnalysisRequest:

    >>> report.setAnalysisRequest(sample.UID())
    >>> report.getAnalysisRequest() == sample
    True

The UID accessor should return the raw UID:

    >>> report.getAnalysisRequestUID() == sample.UID()
    True

The title should default to the sample ID:

    >>> report.Title()
    'W-0001'


Setting Contained Samples
.........................

Multi-sample reports can reference multiple samples. Create a second sample:

    >>> sample2 = new_sample(
    ...     client, contact, sampletype, [service_ph])
    >>> sample2.getId()
    'W-0002'

Set contained samples:

    >>> contained_uids = [sample.UID(), sample2.UID()]
    >>> report.setContainedAnalysisRequests(contained_uids)
    >>> len(report.getContainedAnalysisRequests())
    2

Get the UIDs:

    >>> report.getContainedAnalysisRequestUIDs() == contained_uids
    True


Report Metadata
...............

The metadata field stores report metadata as a plain dict for compatibility
with senaite.impress and the AT-based ARReport.

This is how senaite.impress sets metadata:

    >>> metadata = {
    ...     "template": "senaite.impress:Default",
    ...     "paperformat": "A4",
    ...     "orientation": "portrait",
    ...     "timestamp": "2025-01-15T10:30:00",
    ...     "contained_requests": "W-0001,W-0002"
    ... }

Set metadata using the setter (accepts dict):

    >>> report.setMetadata(metadata)

Get metadata using the getter (returns dict):

    >>> result = report.getMetadata()
    >>> result["template"]
    'senaite.impress:Default'

    >>> result["paperformat"]
    'A4'

    >>> result["orientation"]
    'portrait'

    >>> result["timestamp"]
    '2025-01-15T10:30:00'

Verify the internal storage is a dict:

    >>> raw = report.getRawMetadata()
    >>> isinstance(raw, dict)
    True

    >>> len(raw)
    5

    >>> raw["template"]
    'senaite.impress:Default'

The AT-style property should also work:

    >>> report.Metadata == result
    True


Report Content PDF
..................

Set PDF content:

    >>> pdf_data = b"%PDF-1.4 fake pdf content"
    >>> pdf_file = NamedBlobFile(
    ...     data=pdf_data,
    ...     filename=u"report.pdf",
    ...     contentType="application/pdf")
    >>> report.setPdf(pdf_file)
    >>> report.getPdf().data == pdf_data
    True

The AT-style property should work:

    >>> report.Pdf.data == pdf_data
    True


Date Printed
............

Set the date when the report was printed:

    >>> print_date = datetime(2025, 1, 15, 10, 30, 0)
    >>> print_date = dtime.to_zone(print_date, dtime.get_os_timezone())
    >>> report.setDatePrinted(print_date)
    >>> report.getDatePrinted() == print_date
    True

The AT-style property should work:

    >>> report.DatePrinted == print_date
    True


Recipients
..........

Recipients are stored as a list of dicts (DataGridField):

    >>> recipients = [
    ...     {
    ...         "UID": contact.UID(),
    ...         "Username": "rita",
    ...         "Fullname": "Rita Mohale",
    ...         "EmailAddress": "rita@happyhills.com",
    ...         "PublicationModes": "email,pdf"
    ...     }
    ... ]

    >>> report.setRecipients(recipients)
    >>> result = report.getRecipients()
    >>> len(result)
    1

    >>> result[0]["Fullname"]
    'Rita Mohale'

The AT-style property should work:

    >>> report.Recipients == result
    True


Send Log
........

The send log tracks email deliveries and is compatible with emailview.py
from senaite.impress. It expects to work with lists of dicts.

Get the current send log (empty initially):

    >>> send_log = report.getSendLog()
    >>> send_log is None or len(send_log) == 0
    True

Simulate how emailview.py writes the send log:

    >>> from datetime import datetime as py_datetime
    >>> timestamp = py_datetime.now()

Create a new send log record (simulating emailview.py):

    >>> new_record = {
    ...     "actor": "admin",
    ...     "actor_fullname": "Admin User",
    ...     "email_send_date": timestamp,
    ...     "email_recipients": ["rita@happyhills.com"],
    ...     "email_responsibles": ["lab@happyhills.com"],
    ...     "email_subject": "Your analysis results for W-0001",
    ...     "email_body": "Please find attached...",
    ...     "email_attachments": ["report.pdf"]
    ... }

Append to existing records (as done in emailview.py):

    >>> records = report.getSendLog() or []
    >>> records.append(new_record)
    >>> report.setSendLog(records)

Verify the send log was written:

    >>> result = report.getSendLog()
    >>> len(result)
    1

    >>> result[0]["actor"]
    'admin'

    >>> result[0]["email_recipients"]
    ['rita@happyhills.com']

Add a second send log entry:

    >>> second_record = {
    ...     "actor": "labmanager",
    ...     "actor_fullname": "Lab Manager",
    ...     "email_send_date": py_datetime.now(),
    ...     "email_recipients": ["client@example.com"],
    ...     "email_responsibles": [],
    ...     "email_subject": "Re-send: Results for W-0001",
    ...     "email_body": "As requested...",
    ...     "email_attachments": ["report.pdf"]
    ... }

    >>> records = report.getSendLog()
    >>> records.append(second_record)
    >>> report.setSendLog(records)

Verify both entries exist:

    >>> result = report.getSendLog()
    >>> len(result)
    2

    >>> result[1]["actor"]
    'labmanager'

The AT-style property should work:

    >>> report.SendLog == result
    True


Catalog Indexing
................

The report should be indexed with searchable text including sample IDs,
metadata, and recipients:

    >>> report.reindexObject()
    >>> brains = catalog({"portal_type": "ResultsReport"})
    >>> brain = [b for b in brains if b.UID == report.UID()][0]
    >>> brain.Title
    'W-0001'

The report should be searchable by sample UID:

    >>> brains = catalog({
    ...     "portal_type": "ResultsReport",
    ...     "sample_uid": sample.UID()
    ... })
    >>> len(brains) >= 1
    True

The searchable text should include sample IDs and email recipients:

    >>> searchable = catalog(
    ...     {"portal_type": "ResultsReport",
    ...      "resultsreport_searchable_text": "W-0001"})
    >>> len(searchable) >= 1
    True

    >>> searchable = catalog(
    ...     {"portal_type": "ResultsReport",
    ...      "resultsreport_searchable_text": "rita@happyhills.com"})
    >>> len(searchable) >= 1
    True


Client Accessor
...............

The report should be able to access its client through the primary sample:

    >>> report.getClient() == client
    True


Empty Metadata Handling
.......................

Setting empty metadata should work correctly:

    >>> report.setMetadata({})
    >>> result = report.getMetadata()
    >>> result == {}
    True

Setting None should also work:

    >>> report.setMetadata(None)
    >>> result = report.getMetadata()
    >>> result == {}
    True

Restore metadata for subsequent tests:

    >>> report.setMetadata(metadata)


Simulating senaite.impress Storage Pattern
...........................................

This simulates how senaite.impress creates a complete report through the
storage adapter:

    >>> new_report = api.create(
    ...     sample, "ResultsReport", id="report-002")

    >>> html = "<html><body><h1>Complete Report</h1></body></html>"
    >>> pdf_data = b"%PDF-1.4 complete report"
    >>> pdf = NamedBlobFile(
    ...     data=pdf_data,
    ...     filename=u"complete.pdf",
    ...     contentType="application/pdf")

    >>> metadata = {
    ...     "template": "senaite.impress:MultiDefault",
    ...     "paperformat": "A4",
    ...     "orientation": "landscape",
    ...     "timestamp": DateTime().ISO(),
    ...     "contained_requests": ",".join([sample.getId(), sample2.getId()])
    ... }

Set all fields as senaite.impress would:

    >>> new_report.setAnalysisRequest(sample.UID())
    >>> new_report.setContainedAnalysisRequests(
    ...     [sample.UID(), sample2.UID()])
    >>> new_report.setPdf(pdf)
    >>> new_report.setMetadata(metadata)
    >>> new_report.setDatePrinted(datetime.now())

Verify everything was set correctly:

    >>> new_report.getAnalysisRequest() == sample
    True

    >>> len(new_report.getContainedAnalysisRequests())
    2

    >>> new_report.getPdf().data == pdf_data
    True

    >>> meta = new_report.getMetadata()
    >>> meta["template"]
    'senaite.impress:MultiDefault'

    >>> meta["orientation"]
    'landscape'

Commit and verify the report is persisted:

    >>> transaction.commit()
    >>> catalog = api.get_tool(REPORT_CATALOG)
    >>> brains = catalog({"portal_type": "ResultsReport"})
    >>> len(brains) >= 2
    True


Edge Cases
..........

Test getting metadata when none is set:

    >>> edge_report = api.create(sample, "ResultsReport")
    >>> edge_report.getMetadata()
    {}

Test getting send log when none is set:

    >>> edge_report.getSendLog() is None or len(edge_report.getSendLog()) == 0
    True

Test getting recipients when none are set:

    >>> edge_report.getRecipients() is None or len(edge_report.getRecipients()) == 0
    True


Printing Workflow
.................

The printing workflow allows lab managers to track when results reports have
been printed. When enabled, a "Print Sample" action becomes available for
published samples, which sets the `date_printed` field on the most recent report.

Enable the printing workflow and self-verification in setup:

    >>> setup.setPrintingWorkflowEnabled(True)
    >>> setup.getPrintingWorkflowEnabled()
    True

    >>> setup.setSelfVerificationEnabled(True)

Create a new sample for testing the printing workflow:

    >>> sample_print = new_sample(
    ...     client, contact, sampletype, [service_ph])
    >>> sample_print.getId()
    'W-0003'

The sample starts in sample_due state:

    >>> api.get_workflow_status_of(sample_print)
    'sample_due'

Receive the sample:

    >>> _ = doActionFor(sample_print, "receive")
    >>> api.get_workflow_status_of(sample_print)
    'sample_received'

Submit and verify the analyses:

    >>> for analysis in sample_print.getAnalyses(full_objects=True):
    ...     analysis.setResult("7.5")
    ...     _ = doActionFor(analysis, "submit")
    ...     _ = doActionFor(analysis, "verify")

Check the sample is now verified:

    >>> api.get_workflow_status_of(sample_print)
    'verified'

Create a results report for the sample (as `senaite.impress` would do):

    >>> report_print = api.create(
    ...     sample_print, "ResultsReport", id="report-print-001")
    >>> report_print.setSample(sample_print.UID())
    >>> pdf_data = b"%PDF-1.4 report for printing"
    >>> report_print.setPdf(NamedBlobFile(
    ...     data=pdf_data,
    ...     filename=u"report.pdf",
    ...     contentType="application/pdf"))

Publish the sample (this transitions the sample and all its analyses):

    >>> _ = doActionFor(sample_print, "publish")
    >>> api.get_workflow_status_of(sample_print)
    'published'

At this point, the report has no DatePrinted set:

    >>> report_print.getDatePrinted() is None
    True

Now simulate the "Print Sample" workflow action. This action is triggered
when a user clicks "Print Sample" in the sample listing or view. The action
sets the `date_printed` field on the most recent report:

    >>> from DateTime import DateTime
    >>> report_print.setDatePrinted(
    ...     DateTime().asdatetime().replace(tzinfo=None))

After setting the DatePrinted (as the print_sample action does), verify it:

    >>> report_print.getDatePrinted() is not None
    True

The `date_printed` should be a datetime object:

    >>> from datetime import datetime as py_datetime
    >>> isinstance(report_print.getDatePrinted(), py_datetime)
    True


Relationship Keys and getRawReports
....................................

The ResultsReport schema uses relationship keys that allow samples to look up
their associated reports via getRawReports(). This uses the backreference
mechanism from the UIDReferenceField relationships.

Test the primary sample relationship:

    >>> raw_reports = sample_print.getRawReports()
    >>> report_print.UID() in raw_reports
    True

Create another sample and a multi-sample report:

    >>> sample_multi1 = new_sample(
    ...     client, contact, sampletype, [service_ph])
    >>> sample_multi1.getId()
    'W-0004'

    >>> sample_multi2 = new_sample(
    ...     client, contact, sampletype, [service_temp])
    >>> sample_multi2.getId()
    'W-0005'

Receive, submit, verify, and publish both samples:

    >>> for sample_obj in [sample_multi1, sample_multi2]:
    ...     _ = doActionFor(sample_obj, "receive")
    ...     for analysis in sample_obj.getAnalyses(full_objects=True):
    ...         analysis.setResult("25.0")
    ...         _ = doActionFor(analysis, "submit")
    ...         _ = doActionFor(analysis, "verify")
    ...     _ = doActionFor(sample_obj, "publish")

Create a multi-sample report with sample_multi1 as primary and both samples
as contained samples:

    >>> multi_report = api.create(
    ...     sample_multi1, "ResultsReport", id="report-multi-001")
    >>> multi_report.setSample(sample_multi1.UID())
    >>> multi_report.setContainedSamples(
    ...     [sample_multi1.UID(), sample_multi2.UID()])
    >>> multi_report.setPdf(NamedBlobFile(
    ...     data=b"%PDF-1.4 multi-sample report",
    ...     filename=u"multi-report.pdf",
    ...     contentType="application/pdf"))
    >>> transaction.commit()

The primary sample should find the report via the primary relationship:

    >>> raw_reports_1 = sample_multi1.getRawReports()
    >>> multi_report.UID() in raw_reports_1
    True

The contained sample should also find the report via the contained
samples relationship:

    >>> raw_reports_2 = sample_multi2.getRawReports()
    >>> multi_report.UID() in raw_reports_2
    True

Verify that each sample can retrieve the multi-report object:

    >>> report_catalog = api.get_tool(REPORT_CATALOG)
    >>> reports_for_sample1 = [api.get_object(uid) for uid in raw_reports_1]
    >>> multi_report in reports_for_sample1
    True

    >>> reports_for_sample2 = [api.get_object(uid) for uid in raw_reports_2]
    >>> multi_report in reports_for_sample2
    True

Test the print workflow with the multi-sample report:

    >>> multi_report.getDatePrinted() is None
    True

Simulate printing the primary sample (this sets DatePrinted on the report):

    >>> multi_report.setDatePrinted(
    ...     DateTime().asdatetime().replace(tzinfo=None))
    >>> multi_report.getDatePrinted() is not None
    True

The report should still be findable via both samples after printing:

    >>> multi_report.UID() in sample_multi1.getRawReports()
    True

    >>> multi_report.UID() in sample_multi2.getRawReports()
    True


Backward Compatibility with Old Field Names
............................................

The refactored ResultsReport maintains backward compatibility with the old
field names "analysis_request" and "contained_analysis_requests".

Test that the old getter methods work with deprecation warnings:

    >>> report_compat = api.create(
    ...     sample, "ResultsReport", id="report-compat-001")
    >>> report_compat.setAnalysisRequest(sample.UID())

The old getter should return the same object as the new getter:

    >>> report_compat.getAnalysisRequest() == report_compat.getSample()
    True

    >>> report_compat.getAnalysisRequest() == sample
    True

Test the old setter and getter for contained samples:

    >>> report_compat.setContainedAnalysisRequests(
    ...     [sample.UID(), sample2.UID()])
    >>> len(report_compat.getContainedAnalysisRequests())
    2

    >>> report_compat.getContainedAnalysisRequests() == \
    ...     report_compat.getContainedSamples()
    True

Test the old UID getters:

    >>> report_compat.getAnalysisRequestUID() == sample.UID()
    True

    >>> report_compat.getAnalysisRequestUID() == \
    ...     report_compat.getSampleUID()
    True

    >>> uids = report_compat.getContainedAnalysisRequestUIDs()
    >>> uids == report_compat.getContainedSampleUIDs()
    True

    >>> len(uids)
    2

Test the old AT-style properties:

    >>> report_compat.AnalysisRequest == report_compat.Sample
    True

    >>> report_compat.ContainedAnalysisRequests == \
    ...     report_compat.ContainedSamples
    True

Test the raw accessors:

    >>> report_compat.getRawAnalysisRequest() == \
    ...     report_compat.getRawSample()
    True

    >>> report_compat.getRawContainedAnalysisRequests() == \
    ...     report_compat.getRawContainedSamples()
    True

Verify that setting via old names updates the new fields:

    >>> test_report = api.create(
    ...     sample, "ResultsReport", id="report-test-001")
    >>> test_report.setAnalysisRequest(sample2.UID())
    >>> test_report.getSample() == sample2
    True

    >>> test_report.setContainedAnalysisRequests([sample.UID()])
    >>> test_report.getContainedSamples()[0] == sample
    True
