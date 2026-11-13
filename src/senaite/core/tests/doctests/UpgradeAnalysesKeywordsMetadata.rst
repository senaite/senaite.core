Upgrade: analyses keywords metadata
-----------------------------------

The 2.7.0 upgrade fills the `getAnalysesKeywords` metadata of the samples
catalog for the existing samples.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t UpgradeAnalysesKeywordsMetadata


Test Setup
..........

Needed Imports:

    >>> from DateTime import DateTime
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import logout
    >>> from plone.app.testing import setRoles
    >>> from senaite.core.catalog import SAMPLE_CATALOG
    >>> from senaite.core.upgrade.v02_07_000 import add_sample_analyses_keywords_metadata

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = portal.bika_setup
    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])

A sample with two analyses:

    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Category=category.UID())
    >>> Fe = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Iron", Keyword="Fe", Category=category.UID())
    >>> values = {
    ...     "Client": client.UID(),
    ...     "Contact": contact.UID(),
    ...     "DateSampled": DateTime().strftime("%Y-%m-%d"),
    ...     "SampleType": sampletype.UID()}
    >>> sample = create_analysisrequest(client, request, values, [Cu.UID(), Fe.UID()])


Refreshing the metadata
.......................

An earlier step adds the column without a value for the existing samples:

    >>> catalog = api.get_tool(SAMPLE_CATALOG)
    >>> catalog.delColumn("getAnalysesKeywords")
    >>> catalog.addColumn("getAnalysesKeywords")
    >>> brain = catalog.unrestrictedSearchResults(UID=api.get_uid(sample))[0]
    >>> isinstance(brain.getAnalysesKeywords, (list, tuple))
    False

The step refreshes the samples without a value, whoever runs the upgrade:

    >>> logout()
    >>> add_sample_analyses_keywords_metadata(portal.portal_setup)

    >>> brain = catalog.unrestrictedSearchResults(UID=api.get_uid(sample))[0]
    >>> sorted(brain.getAnalysesKeywords)
    ['Cu', 'Fe']
