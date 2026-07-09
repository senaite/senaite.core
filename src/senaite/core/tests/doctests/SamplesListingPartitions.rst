Samples listing partition visibility
------------------------------------

The samples listing shows sample partitions nested under their primary
sample. A partition is only listed as a top-level row when its primary
is not part of the same result set, e.g. when a single partition is
dispatched while its primary sample stays active. This keeps the
pagination counts correct because the filtering happens at search time,
before the result is counted and sliced.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t SamplesListingPartitions


Test Setup
..........

Imports:

    >>> from DateTime import DateTime
    >>> from bika.lims import api
    >>> from senaite.core.catalog import SAMPLE_CATALOG
    >>> from senaite.core.browser.samples.view import SamplesView
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.analysisrequest import create_partition
    >>> from bika.lims.workflow import doActionFor as do_action_for

Functional helpers:

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

Variables:

    >>> date_now = timestamp()
    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bika_setup = portal.bika_setup
    >>> sampletypes = setup.sampletypes
    >>> analysiscategories = setup.analysiscategories
    >>> bika_analysisservices = bika_setup.bika_analysisservices

Test user — Lab Manager:

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager', 'LabManager'])


Setup Client, Contact, SampleType and AnalysisService
.....................................................

    >>> clients = self.portal.clients
    >>> client = api.create(clients, "Client", Name="ACME", ClientID="A")
    >>> contact = api.create(client, "Contact", Firstname="John", Surname="Doe")
    >>> sampletype = api.create(sampletypes, "SampleType",
    ...     Prefix="water", MinimumVolume="100 ml")
    >>> category = api.create(analysiscategories, "AnalysisCategory",
    ...     title="Water")
    >>> service = api.create(bika_analysisservices, "AnalysisService",
    ...     title="PH", ShortTitle="ph", Category=category, Keyword="PH")


Create a primary sample with two partitions
............................................

    >>> values = {
    ...     "Client": client.UID(),
    ...     "Contact": contact.UID(),
    ...     "SamplingDate": date_now,
    ...     "DateSampled": date_now,
    ...     "SampleType": sampletype.UID(),
    ... }
    >>> primary = create_analysisrequest(client, request, values,
    ...                                  [service.UID()])
    >>> part1 = create_partition(primary, request, primary.getAnalyses())
    >>> part2 = create_partition(primary, request, primary.getAnalyses())


`hide_nested_partitions` keeps only samples listed on their own
...............................................................

    >>> view = SamplesView(portal, request)

Helper to fetch brains for a set of samples and run the filter:

    >>> catalog = api.get_tool(SAMPLE_CATALOG)
    >>> def visible_ids(samples):
    ...     uids = [api.get_uid(s) for s in samples]
    ...     brains = catalog(UID=uids)
    ...     visible = view.hide_nested_partitions(brains)
    ...     return sorted([api.get_id(b) for b in visible])

When the primary and its partitions are all in the result, only the
primary is listed; the partitions nest under it:

    >>> visible_ids([primary, part1, part2])
    ['water-0001']

When the primary is not part of the result, the partitions are orphaned
and therefore listed on their own:

    >>> visible_ids([part1, part2])
    ['water-0001-P01', 'water-0001-P02']

A single orphaned partition shows up as well:

    >>> visible_ids([part1])
    ['water-0001-P01']


The filter drives the listed-UIDs cache for folderitem
.......................................................

After filtering a full result set, only the primary UID is cached as a
listed row, so a nested partition does not carry a parent reference:

    >>> brains = catalog(UID=[api.get_uid(primary),
    ...                       api.get_uid(part1), api.get_uid(part2)])
    >>> _ = view.hide_nested_partitions(brains)
    >>> api.get_uid(primary) in view._listed_uids
    True
    >>> api.get_uid(part1) in view._listed_uids
    False


Flat listings render every sample on its own, without nesting
.............................................................

Some review states (e.g. the dispatched/disposed pools, or the stored
samples added by senaite.storage) are flat pools: every matching sample,
partitions included, is shown as a top-level row. Such a state carries a
`flat_listing` flag:

    >>> view = SamplesView(portal, request)
    >>> state_key = "%s_review_state" % view.form_id

    >>> request.form[state_key] = "dispatched"
    >>> view.flat_listing
    True

A flat listing disables the partition nesting, so `folderitem` wires up no
parent/children references:

    >>> view.show_partitions
    False

A regular review state keeps the orphan-nesting behavior:

    >>> request.form[state_key] = "default"
    >>> view.flat_listing
    False
    >>> view.show_partitions
    True
