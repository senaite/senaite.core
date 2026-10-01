Publish on report stored
------------------------

The samples of a results report are published as soon as the report exists,
not when an email is sent. senaite.impress hands the stored reports over to
the `IReportStoredHandler` adapter, and senaite.core transitions the samples
in it.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t PublishOnReportStored


Test Setup
..........

Needed Imports:

    >>> import transaction

    >>> from DateTime import DateTime
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> from plone.namedfile.file import NamedBlobFile
    >>> from senaite.core.interfaces import IReportStoredHandler
    >>> from zope.component import queryMultiAdapter

Functional Helpers:

    >>> def new_sample(services):
    ...     values = {
    ...         "Client": client.UID(),
    ...         "Contact": contact.UID(),
    ...         "DateSampled": DateTime().strftime("%Y-%m-%d"),
    ...         "SampleType": sampletype.UID(),
    ...     }
    ...     service_uids = [s.UID() for s in services]
    ...     return create_analysisrequest(
    ...         client, request, values, service_uids)

    >>> def receive(sample):
    ...     ignored = doActionFor(sample, "receive")
    ...     return api.get_review_status(sample)

    >>> def new_report(sample, contained=None):
    ...     pdf = NamedBlobFile(data=b"%PDF-1.4 fake",
    ...                         filename=u"report.pdf",
    ...                         contentType="application/pdf")
    ...     uids = map(api.get_uid, contained or [sample])
    ...     return api.create(sample, "ResultsReport",
    ...                       sample=api.get_uid(sample),
    ...                       contained_samples=uids, pdf=pdf, metadata={})

    >>> def submit(sample):
    ...     for analysis in sample.getAnalyses(full_objects=True):
    ...         analysis.setResult(5)
    ...         ignored = doActionFor(analysis, "submit")
    ...     return api.get_review_status(sample)

    >>> def submit_and_verify(sample):
    ...     for analysis in sample.getAnalyses(full_objects=True):
    ...         analysis.setResult(5)
    ...         ignored = doActionFor(analysis, "submit")
    ...         ignored = doActionFor(analysis, "verify")
    ...     return api.get_review_status(sample)

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bika_setup = portal.bika_setup

Grant the required privileges:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager", "Manager"])
    >>> transaction.commit()

Allow the same user to verify the results submitted:

    >>> bika_setup.setSelfVerificationEnabled(True)

LIMS setup:

    >>> client = api.create(
    ...     portal.clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(
    ...     client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(
    ...     setup.sampletypes, "SampleType", title="Water", Prefix="W")
    >>> category = api.create(
    ...     setup.analysiscategories, "AnalysisCategory", title="Chemistry")
    >>> service = api.create(
    ...     bika_setup.bika_analysisservices, "AnalysisService", title="pH",
    ...     Category=category, Keyword="PH")


The handler is registered
.........................

senaite.core registers the default handler, so the storage adapter of
senaite.impress finds one when it hands the stored reports over:

    >>> handler = queryMultiAdapter((client, request), IReportStoredHandler)
    >>> handler.__class__.__name__
    'PublishSamplesHandler'


A verified sample is published when the report is stored
........................................................

    >>> sample = new_sample([service])
    >>> receive(sample)
    'sample_received'
    >>> submit_and_verify(sample)
    'verified'

Hand a report for it over to the handler, the way the storage adapter does:

    >>> handler([new_report(sample)])

The sample is published, without sending any email:

    >>> api.get_review_status(sample)
    'published'


A second report republishes the sample
......................................

    >>> handler([new_report(sample)])
    >>> api.get_review_status(sample)
    'published'

The workflow history tells the two apart:

    >>> actions = [item.get("action") for item
    ...            in api.get_review_history(sample)]
    >>> "publish" in actions and "republish" in actions
    True


A sample that is not verified yet is prepublished
.................................................

Results submitted, but not verified:

    >>> sample = new_sample([service])
    >>> receive(sample)
    'sample_received'
    >>> submit(sample)
    'to_be_verified'

    >>> handler([new_report(sample)])

`prepublish` does not change the status of the sample, it only marks the
results as preliminarily published:

    >>> api.get_review_status(sample)
    'to_be_verified'

    >>> actions = [item.get("action") for item
    ...            in api.get_review_history(sample)]
    >>> "prepublish" in actions
    True


A sample without submitted results is left alone
................................................

The guard of `prepublish` requires at least one submitted analysis, so a
report for a sample without results transitions nothing:

    >>> sample = new_sample([service])
    >>> receive(sample)
    'sample_received'

    >>> handler([new_report(sample)])
    >>> api.get_review_status(sample)
    'sample_received'


Contained samples are published as well
.......................................

A report may contain more than one sample, all of them are published:

    >>> sample_a = new_sample([service])
    >>> sample_b = new_sample([service])
    >>> receive(sample_a)
    'sample_received'
    >>> receive(sample_b)
    'sample_received'
    >>> submit_and_verify(sample_a)
    'verified'
    >>> submit_and_verify(sample_b)
    'verified'

    >>> handler([new_report(sample_a, [sample_a, sample_b])])

    >>> api.get_review_status(sample_a)
    'published'
    >>> api.get_review_status(sample_b)
    'published'
