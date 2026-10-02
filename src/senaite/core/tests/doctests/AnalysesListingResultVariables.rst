Result variables in the analyses listing
----------------------------------------

Result variables (interims) with choices set are rendered as a selection
list. Whether an empty option is offered depends on the `allow_empty`
setting of the result variable.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t AnalysesListingResultVariables


Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.browser.analyses.view import AnalysesView
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID

Functional Helpers:

    >>> def new_sample(services):
    ...     values = {
    ...         "Client": client.UID(),
    ...         "Contact": contact.UID(),
    ...         "DateSampled": date_now,
    ...         "SampleType": sampletype.UID()}
    ...     service_uids = map(api.get_uid, services)
    ...     sample = create_analysisrequest(client, request, values, service_uids)
    ...     transitioned = do_action_for(sample, "receive")
    ...     return sample

    >>> def get_choices(sample, keyword):
    ...     view = AnalysesView(sample, request)
    ...     view.update()
    ...     items = view.folderitems()
    ...     choices = items[0].get("choices", {}).get(keyword, [])
    ...     return [choice["ResultValue"] for choice in choices]

    >>> def set_interim(analysis, **kwargs):
    ...     interim = {"keyword": "interim_1", "title": "Interim 1"}
    ...     interim.update(kwargs)
    ...     analysis.setInterimFields([interim])

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = portal.bika_setup
    >>> date_now = DateTime().strftime("%Y-%m-%d")

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Category=category.UID())


Multi-valued result variables
.............................

Create a sample and set a multi-valued result variable that does not allow
empty values. No empty option is offered, so the analyst is forced to select
at least one of the choices:

    >>> sample = new_sample([Cu])
    >>> analysis = sample.getAnalyses(full_objects=True)[0]
    >>> set_interim(analysis, result_type="multiselect",
    ...             choices="1:Option 1|2:Option 2", allow_empty=False)
    >>> get_choices(sample, "interim_1")
    ['1', '2']

When the result variable allows empty values, the empty option is offered.
Dexterity types store this setting as a boolean:

    >>> set_interim(analysis, result_type="multiselect",
    ...             choices="1:Option 1|2:Option 2", allow_empty=True)
    >>> get_choices(sample, "interim_1")
    ['', '1', '2']

While the Archetypes' records widget submits it as `"on"`:

    >>> set_interim(analysis, result_type="multiselect",
    ...             choices="1:Option 1|2:Option 2", allow_empty="on")
    >>> get_choices(sample, "interim_1")
    ['', '1', '2']

A result variable for which the setting was never submitted does not allow
empty values:

    >>> set_interim(analysis, result_type="multiselect",
    ...             choices="1:Option 1|2:Option 2")
    >>> get_choices(sample, "interim_1")
    ['1', '2']


Single-valued result variables
..............................

For single-valued result variables without a value set, the empty option is
always offered, so the default value is not silently captured as a result:

    >>> set_interim(analysis, result_type="select",
    ...             choices="1:Option 1|2:Option 2", allow_empty=False)
    >>> get_choices(sample, "interim_1")
    ['', '1', '2']

But not when a value is already set and empty values are not allowed:

    >>> set_interim(analysis, result_type="select", value="2",
    ...             choices="1:Option 1|2:Option 2", allow_empty=False)
    >>> get_choices(sample, "interim_1")
    ['1', '2']

    >>> set_interim(analysis, result_type="select", value="2",
    ...             choices="1:Option 1|2:Option 2", allow_empty=True)
    >>> get_choices(sample, "interim_1")
    ['', '1', '2']
