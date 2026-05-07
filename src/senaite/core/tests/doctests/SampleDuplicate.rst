Sample duplicate
----------------

The `duplicate` workflow transition creates a sibling Sample
directly (no add form). The duplicate uses the regular Sample ID
format (i.e. shares the same counter as plain samples), but is
identifiable as a duplicate via the `IAnalysisRequestDuplicate`
marker interface and the `DuplicatedFrom` reference back to the
source.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t SampleDuplicate


Test Setup
..........

Imports:

    >>> from DateTime import DateTime
    >>> from bika.lims import api
    >>> from bika.lims.interfaces import IAnalysisRequestDuplicate
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.analysisrequest import create_duplicate_of
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


Create the source Sample
........................

    >>> values = {
    ...     "Client": client.UID(),
    ...     "Contact": contact.UID(),
    ...     "SamplingDate": date_now,
    ...     "DateSampled": date_now,
    ...     "SampleType": sampletype.UID(),
    ... }
    >>> source = create_analysisrequest(client, request, values,
    ...                                 [service.UID()])
    >>> source
    <AnalysisRequest at /plone/clients/client-1/water-0001>


Duplicate via the factory
.........................

`create_duplicate_of` produces a sibling marked with
`IAnalysisRequestDuplicate` whose `DuplicatedFrom` points back at
the source. The duplicate gets a fresh Sample ID from the regular
sample counter:

    >>> dup = create_duplicate_of(source)
    >>> dup
    <AnalysisRequest at /plone/clients/client-1/water-0002>

    >>> IAnalysisRequestDuplicate.providedBy(dup)
    True

    >>> dup.getDuplicatedFrom() == source
    True


The source's workflow state is unchanged:

    >>> api.get_workflow_status_of(source)
    'sample_due'


Duplicate analyses are recreated empty
......................................

The duplicate has the same analysis services but no results:

    >>> sorted([a.getKeyword() for a in dup.getAnalyses(full_objects=True)])
    ['PH']

    >>> [a.getResult() for a in dup.getAnalyses(full_objects=True)]
    ['']


Counter advances on subsequent duplicates
.........................................

Each duplicate gets the next ID from the regular sample counter:

    >>> dup2 = create_duplicate_of(source)
    >>> api.get_id(dup2)
    'water-0003'

    >>> dup3 = create_duplicate_of(source)
    >>> api.get_id(dup3)
    'water-0004'


Duplicate via the workflow transition
.....................................

The same outcome is achievable via the `duplicate` transition,
which fires the `after_duplicate` event:

    >>> succeeded, message = do_action_for(source, "duplicate")
    >>> succeeded
    True


The source remains in its previous state after the transition
(``new_state`` is empty):

    >>> api.get_workflow_status_of(source)
    'sample_due'


Duplicates honour a custom ID Server schema
...........................................

Duplicates do not use a dedicated ID template; they share the
`AnalysisRequest` ID format and counter. So when an integrator
customises the `AnalysisRequest` template through the ID Server
admin, duplicates render with the same shape as plain samples.

Override the `AnalysisRequest` template:

    >>> senaite_setup = api.get_senaite_setup()
    >>> formatting = list(senaite_setup.getIDFormatting() or [])
    >>> for record in formatting:
    ...     if record.get("portal_type") == "AnalysisRequest":
    ...         record["form"] = "{sampleType}-{year}-{seq:03d}"
    >>> senaite_setup.setIDFormatting(formatting)

A new source sample now gets the customised ID:

    >>> custom_source = create_analysisrequest(client, request, values,
    ...                                        [service.UID()])
    >>> year = DateTime().strftime("%y")
    >>> api.get_id(custom_source) == "water-{}-001".format(year)
    True

Duplicates of that source pick up the same template:

    >>> custom_dup = create_duplicate_of(custom_source)
    >>> api.get_id(custom_dup) == "water-{}-002".format(year)
    True

    >>> IAnalysisRequestDuplicate.providedBy(custom_dup)
    True

    >>> custom_dup.getDuplicatedFrom() == custom_source
    True

Subsequent duplicates continue along the same counter:

    >>> custom_dup2 = create_duplicate_of(custom_source)
    >>> api.get_id(custom_dup2) == "water-{}-003".format(year)
    True
