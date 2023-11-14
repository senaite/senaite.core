Sample - Auto-receive
---------------------

When the setup setting "Auto-receive samples" is enabled, the system
automatically transitions the sample to "received" status on creation, as long
as the user has the permission `senaite.core: Transition: Receive` granted.

Test Setup
..........

Running this test from the buildout directory:

    bin/test -t SampleAutoReceive

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
    ...     return sample

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.bika_setup
    >>> date_now = DateTime().strftime("%Y-%m-%d")

Create some baseline objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(setup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(setup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(setup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())


Sample auto-receive enabled
...........................

This test validates that when "Auto-receive samples" setting is enabled, the
sample **does** transition automatically to "received" status.

Enable the automatic reception of samples:

    >>> setup.setAutoreceiveSamples(True)
    >>> setup.getAutoreceiveSamples()
    True

Create a Sample:

    >>> sample = new_sample([Cu, Fe, Au])

The status of the analyses is "received":

    >>> api.get_review_status(sample)
    'sample_received'


Sample auto-receive disabled
.................................

This test validates that when "Auto-receive samples" setting is disabled, the
sample does not transition automatically to "received" status.

Disable the automatic reception of samples:

    >>> setup.setAutoreceiveSamples(False)
    >>> setup.getAutoreceiveSamples()
    False

Create a Sample:

    >>> sample = new_sample([Cu, Fe, Au])

The sample remains in "sample_due" status:

    >>> api.get_review_status(sample)
    'sample_due'

Manual reception of the sample is required:

    >>> success = do_action_for(sample, "receive")
    >>> api.get_review_status(sample)
    'sample_received'
