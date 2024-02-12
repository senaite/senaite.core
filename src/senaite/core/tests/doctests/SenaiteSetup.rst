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
    >>> sampletype = api.create(bikasetup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(bikasetup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
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



Email body for sample publication
.................................

Initially, the field is empty and should return the default value:

    >>> from senaite.core.content.senaitesetup import default_email_body_sample_publication
    >>> senaite_setup.getEmailBodySamplePublication() == default_email_body_sample_publication(senaite_setup)
    True

A new value can be set via the provided setter:

    >>> senaite_setup.setEmailBodySamplePublication("Your results are there!")
    >>> senaite_setup.getEmailBodySamplePublication()
    u'Your results are there!'

The old setup provides proxy fields to get/set the value:

    >>> bikasetup.getEmailBodySamplePublication() == senaite_setup.getEmailBodySamplePublication()
    True

    >>> bikasetup.setEmailBodySamplePublication("Changes done via old setup UI")
    >>> bikasetup.getEmailBodySamplePublication()
    u'Changes done via old setup UI'

    >>> bikasetup.getEmailBodySamplePublication() == senaite_setup.getEmailBodySamplePublication()
    True
