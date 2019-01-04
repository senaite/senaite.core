Analysis Request to_be_sampled guard and event
==============================================

Running this test from the buildout directory:

    bin/test test_textual_doctests -t WorkflowAnalysisRequestToBeSampled

Test Setup
----------

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from bika.lims.workflow import getAllowedTransitions
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

    >>> def new_ar(services, ar_template=None):
    ...     values = {
    ...         'Client': client.UID(),
    ...         'Contact': contact.UID(),
    ...         'DateSampled': date_now,
    ...         'SampleType': sampletype.UID(),
    ...         'Template': ar_template,
    ...     }
    ...     service_uids = map(api.get_uid, services)
    ...     ar = create_analysisrequest(client, request, values, service_uids)
    ...     return ar

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> bikasetup = portal.bika_setup
    >>> date_now = timestamp()

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH", MemberDiscountApplies=True)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(bikasetup.bika_sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(bikasetup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(bikasetup.bika_analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Price="15", Category=category.UID(), Accredited=True)
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Price="10", Category=category.UID())
    >>> Au = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Gold", Keyword="Au", Price="20", Category=category.UID())
    >>> ar_template = api.create(bikasetup.bika_artemplates, "ARTemplate", title="Test Template", SampleType=sampletype)

To_be_sampled transition and guard basic constraints
----------------------------------------------------

Create an Analysis Request:

    >>> ar = new_ar([Cu])

By default, the Analysis Request transitions to "sample_due" status:

    >>> api.get_workflow_status_of(ar)
    'sample_due'

But if the setup setting "SamplingWorkflowEnabled" is set to True, the status
of the Analysis Request once created is "to_be_sampled":

    >>> bikasetup.setSamplingWorkflowEnabled(True)
    >>> ar = new_ar([Cu])
    >>> api.get_workflow_status_of(ar)
    'to_be_sampled'

If we use a template with "SamplingRequired" setting set to False, the status
of the Analysis Request once created is "sample_due", regardless of the setting
from setup:

    >>> ar_template.setSamplingRequired(False)
    >>> ar = new_ar([Cu], ar_template)
    >>> api.get_workflow_status_of(ar)
    'sample_due'

And same the other way round:

    >>> bikasetup.setSamplingWorkflowEnabled(False)
    >>> ar_template.setSamplingRequired(True)
    >>> ar = new_ar([Cu], ar_template)
    >>> api.get_workflow_status_of(ar)
    'to_be_sampled'
