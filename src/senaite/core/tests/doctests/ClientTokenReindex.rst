Client Token Reindex
--------------------

Client contacts find the content of their client in the catalogs by the
`client:<uid>` token in the `allowedRolesAndUsers` index. The upgrade to
2.7 adds the token to the existing content with a reindex of that index on
all client-tree objects.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t ClientTokenReindex


Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from senaite.core.catalog import ANALYSIS_CATALOG
    >>> from senaite.core.catalog import SAMPLE_CATALOG
    >>> from senaite.core.upgrade.v02_07_000 import \
    ...     reindex_client_tree_allowed_roles

Functional Helpers:

    >>> def get_tokens(obj, catalog_id):
    ...     catalog = api.get_tool(catalog_id)
    ...     brain = catalog.unrestrictedSearchResults(UID=api.get_uid(obj))[0]
    ...     index = catalog._catalog.getIndex("allowedRolesAndUsers")
    ...     return index.getEntryForObject(brain.getRID()) or []

    >>> def drop_tokens(obj, catalog_id):
    ...     catalog = api.get_tool(catalog_id)
    ...     brain = catalog.unrestrictedSearchResults(UID=api.get_uid(obj))[0]
    ...     index = catalog._catalog.getIndex("allowedRolesAndUsers")
    ...     index.unindex_object(brain.getRID())

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = portal.bika_setup
    >>> date_now = DateTime().strftime("%Y-%m-%d")

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager", "Sampler"])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Water", Prefix="W")
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu")
    >>> values = {
    ...     "Client": client.UID(),
    ...     "Contact": contact.UID(),
    ...     "DateSampled": date_now,
    ...     "SampleType": sampletype.UID()}
    >>> sample = create_analysisrequest(client, request, values, [Cu.UID()])
    >>> analysis = sample.getAnalyses(full_objects=True)[0]
    >>> token = "client:{}".format(client.UID())


Reindex of the client tree
..........................

A new sample and its analyses carry the token of their client:

    >>> token in get_tokens(sample, SAMPLE_CATALOG)
    True

    >>> token in get_tokens(analysis, ANALYSIS_CATALOG)
    True

Content indexed before the upgrade does not carry the token:

    >>> drop_tokens(sample, SAMPLE_CATALOG)
    >>> drop_tokens(analysis, ANALYSIS_CATALOG)

    >>> token in get_tokens(sample, SAMPLE_CATALOG)
    False

    >>> token in get_tokens(analysis, ANALYSIS_CATALOG)
    False

The reindex of the upgrade step adds it again:

    >>> reindex_client_tree_allowed_roles()

    >>> token in get_tokens(sample, SAMPLE_CATALOG)
    True

    >>> token in get_tokens(analysis, ANALYSIS_CATALOG)
    True
