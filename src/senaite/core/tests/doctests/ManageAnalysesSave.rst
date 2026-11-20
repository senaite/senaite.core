Manage analyses save
--------------------

The "Save" button of the "Manage analyses" view of a sample sets the
analyses of the services that are selected, and removes the rest. Unless the
setup requires at least one analysis per sample, the button is also displayed
when no service is selected, so all the analyses can be removed.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t ManageAnalysesSave


Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.browser.analysisrequest.manage_analyses import \
    ...     AnalysisRequestAnalysesView
    >>> from bika.lims.browser.workflow.analysisrequest import \
    ...     WorkflowActionSaveAnalysesAdapter
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID

Functional Helpers:

    >>> def new_sample(services):
    ...     values = {
    ...         "Client": client.UID(),
    ...         "Contact": contact.UID(),
    ...         "DateSampled": DateTime().strftime("%Y-%m-%d"),
    ...         "SampleType": sampletype.UID()}
    ...     service_uids = map(api.get_uid, services)
    ...     return create_analysisrequest(client, request, values, service_uids)

    >>> def save_analyses(sample, services):
    ...     # as the "Save" button of "Manage analyses" does, with the services
    ...     # that are selected
    ...     request.form = {
    ...         "workflow_action": "save_analyses",
    ...         "uids": map(api.get_uid, services),
    ...     }
    ...     adapter = WorkflowActionSaveAnalysesAdapter(sample, request)
    ...     adapter("save_analyses", [sample])

    >>> def get_keywords(sample):
    ...     analyses = sample.getAnalyses(full_objects=True)
    ...     return sorted([an.getKeyword() for an in analyses])

    >>> def get_last_message():
    ...     # last status message of the request
    ...     messages = portal.plone_utils.showPortalMessages()
    ...     return messages[-1].message

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_senaite_setup()
    >>> bikasetup = portal.bika_setup

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager",])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Category=category.UID())
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Category=category.UID())


Save button
...........

The "Save" button is displayed when no service is selected, so all the
analyses can be removed:

    >>> setup.setSampleAnalysesRequired(False)
    >>> sample = new_sample([Cu, Fe])
    >>> view = AnalysisRequestAnalysesView(sample, request)
    >>> view.update()
    >>> review_state = view.review_states[0]
    >>> [tr["id"] for tr in review_state["custom_transitions"]]
    ['save_analyses']
    >>> review_state["allow_empty_selection"]
    True

Unless the setup requires at least one analysis per sample:

    >>> setup.setSampleAnalysesRequired(True)
    >>> view = AnalysisRequestAnalysesView(sample, request)
    >>> view.update()
    >>> view.review_states[0]["allow_empty_selection"]
    False


Save with services selected
...........................

The analyses of the services that are not selected are removed:

    >>> setup.setSampleAnalysesRequired(True)
    >>> get_keywords(sample)
    ['Cu', 'Fe']
    >>> save_analyses(sample, [Cu])
    >>> get_keywords(sample)
    ['Cu']


Save with no services selected
..............................

When analyses are required, the sample cannot be left without analyses, even
if the save is submitted with no services selected:

    >>> save_analyses(sample, [])
    >>> get_keywords(sample)
    ['Cu']
    >>> get_last_message()
    u'At least one analysis is required'


When analyses are not required, all the analyses are removed:

    >>> setup.setSampleAnalysesRequired(False)
    >>> save_analyses(sample, [])
    >>> get_keywords(sample)
    []
