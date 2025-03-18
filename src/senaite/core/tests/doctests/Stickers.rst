Stickers
--------

Stickers can be generated for Samples, Reference Samples, Batches and Worksheets.
The default stickers are configured in the Setup, but can be individually set for samples.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t Stickers

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


Global sticker setup
....................

Remember the default stickers:

    >>> DEFAULT_STICKER = "QR_1x14mmx39mm.pt"
    >>> SMALL_STICKER = "Code_39_1x54mm.pt"
    >>> LARGE_STICKER = "Code_39_1x72mm.pt"

Set the default sticker templates for all types:

    >>> bikasetup.setAutoStickerTemplate(DEFAULT_STICKER)
    >>> bikasetup.setSmallStickerTemplate(SMALL_STICKER)
    >>> bikasetup.setLargeStickerTemplate(LARGE_STICKER)

Now we create a Sample:

    >>> sample = new_sample([Cu, Fe, Au], client, contact, sampletype)
    >>> api.get_workflow_status_of(sample)
    'sample_due'

Receive the sample:

    >>> transitioned = do_action_for(sample, "receive")
    >>> api.get_workflow_status_of(sample)
    'sample_received'

The default Sticker template should be set from the setup:

    >>> view = api.get_view("sticker", context=sample, request=request)
    >>> view.get_selected_template() == DEFAULT_STICKER
    True

Now we simulate a browser request to get the **small sticker** template:

    >>> request["size"] = "small"

The default Sticker template should be now set to the **small sticker** from the setup:

    >>> view = api.get_view("sticker", context=sample, request=request)
    >>> view.get_selected_template() == SMALL_STICKER
    True

Now we simulate a browser request to get the **large sticker** template:

    >>> request["size"] = "large"

The default Sticker template should be now set to the **large sticker** from the setup:

    >>> view = api.get_view("sticker", context=sample, request=request)
    >>> view.get_selected_template() == LARGE_STICKER
    True

If an unknown size is requested, the view falls back to the default sticker:

    >>> request["size"] = "jumbo"
    >>> view = api.get_view("sticker", context=sample, request=request)
    >>> view.get_selected_template() == DEFAULT_STICKER
    True


Sample type sticker setup
.........................

We can set admitted stickers in the sample type:

    >>> SAMPLE_TYPE_SMALL_STICKER = "Code_128_1x48mm.pt"
    >>> SAMPLE_TYPE_LARGE_STICKER = "Code_128_1x72mm.pt"

    >>> admitted = [{
    ...     "admitted": [
    ...         SAMPLE_TYPE_SMALL_STICKER,
    ...         SAMPLE_TYPE_LARGE_STICKER,
    ...     ],
    ...     "small_default": SAMPLE_TYPE_SMALL_STICKER,
    ...     "large_default": SAMPLE_TYPE_LARGE_STICKER,
    ... }]
    >>> sampletype.setAdmittedStickerTemplates(admitted)

Although not specified here, the default sticker should default to the setup selected template:

    >>> request["size"] = ""
    >>> view.get_selected_template() == DEFAULT_STICKER
    True

However, the **small sticker** should now come from the sample type:

    >>> request["size"] = "small"
    >>> view.get_selected_template() == SAMPLE_TYPE_SMALL_STICKER
    True


The **large sticker** should also come from the sample type:

    >>> request["size"] = "large"
    >>> view.get_selected_template() == SAMPLE_TYPE_LARGE_STICKER
    True


Type filters
............

Stickers can be filtered by type, e.g. withc `filter_by_type=batch` or `filter_by_type=worksheet`.
When a type filter is set, the sticker view looks up a subfolder with the filtered type name for templates.

For the `batch` type, there is currently only one template available:

    >>> BATCH_STICKER = "Code_39_40x20mm.pt"

    >>> batch = api.create(portal.batches, "Batch", title="Test Batch")
    >>> view = api.get_view("sticker", context=batch, request=request)

    >>> request["filter_by_type"] = "batch"
    >>> view.get_selected_template() == BATCH_STICKER
    True

There should also be no other stickers available:

    >>> len(view.get_available_templates())
    1
