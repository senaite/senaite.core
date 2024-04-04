Sample - Auto-verify
--------------------

When the setup setting "Automatic verification of Samples" is enabled, the
system automatically transitions the sample to "verified" status when all the
analyses it contains are verified. System expects the user to manually verify
the sample otherwise.


Test Setup
..........

Running this test from the buildout directory:

    bin/test -t SampleAutoVerify

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID

Functional Helpers:

    >>> def new_sample(services):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': date_now,
    ...         'SampleType': sampletype.UID()}
    ...     uids = map(api.get_uid, services)
    ...     sample = create_analysisrequest(client, request, values, uids)
    ...     transitioned = do_action_for(sample, "receive")
    ...     return sample

    >>> def submit_results(sample):
    ...     for analysis in sample.getAnalyses(full_objects=True):
    ...         analysis.setResult(10)
    ...         do_action_for(analysis, "submit")

    >>> def verify_results(sample):
    ...     analyses = sample.getAnalyses(full_objects=True)
    ...     map(lambda a: do_action_for(a, "verify"), analyses)

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = portal.bika_setup
    >>> date_now = DateTime().strftime("%Y-%m-%d")


Create some baseline objects for the test:

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

Enable the self verification:

    >>> bikasetup.setSelfVerificationEnabled(True)
    >>> bikasetup.getSelfVerificationEnabled()
    True

Sample auto-verification enabled
................................

This test validates that when "Automatic verification of Samples" setting is
enabled, the sample **does** transition automatically to "verified" status.

Enable the automatic verification of samples:

    >>> bikasetup.setAutoVerifySamples(True)
    >>> bikasetup.getAutoVerifySamples()
    True

Create a Sample, submit and verify results:

    >>> sample = new_sample([Cu, Fe, Au])
    >>> submit_results(sample)
    >>> verify_results(sample)

The status of the analyses is "verified":

    >>> map(api.get_review_status, sample.getAnalyses())
    ['verified', 'verified', 'verified']

And the status of the sample as well:

    >>> api.get_review_status(sample)
    'verified'


Sample auto-verification disabled
.................................

This test validates that when "Automatic verification of Samples" setting is
disabled, the sample does not transition automatically to "verified" status.

Disable the automatic verification of samples:

    >>> bikasetup.setAutoVerifySamples(False)
    >>> bikasetup.getAutoVerifySamples()
    False

Create a Sample, submit and verify results:

    >>> sample = new_sample([Cu, Fe, Au])
    >>> submit_results(sample)
    >>> verify_results(sample)

The status of the analyses is "verified":

    >>> map(api.get_review_status, sample.getAnalyses())
    ['verified', 'verified', 'verified']

But the sample remains in "to_be_verified" status:

    >>> api.get_review_status(sample)
    'to_be_verified'

Manual verification of the sample is required:

    >>> success = do_action_for(sample, "verify")
    >>> api.get_review_status(sample)
    'verified'
