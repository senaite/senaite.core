Sample duplicate
----------------

The `duplicate_sample` workflow transition creates a sibling Sample
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


Auditlog snapshot reflects the copied fields
............................................

A duplicate is one logical create event. The factory suppresses
the partial snapshot that `_processForm` would otherwise write
(the values dict only carries the ID-relevant scalars
Client/Contact/SampleType/Date(Sampled|SamplingDate)) and takes a
single complete snapshot after `copy_field_values` has populated
the rest of the schema. Verify exactly one entry with action
'create':

    >>> from bika.lims.api import snapshot as snap_api
    >>> snap_api.has_snapshots(dup)
    True

    >>> snapshots = snap_api.get_snapshots(dup)
    >>> len(snapshots)
    1

    >>> print(snapshots[0]["__metadata__"]["action"])
    create

The fields that ride the `copy_field_values` path — i.e. fields
NOT in the values dict passed to `create_analysisrequest` — are
the interesting ones, since they're the ones that previously would
have been silently absent from the audit trail. Set a handful on a
fresh source, duplicate, and assert both the duplicate's field
values and its snapshot:

    >>> rich_type = api.create(sampletypes, "SampleType",
    ...     Prefix="rich", MinimumVolume="100 ml")
    >>> rich_values = dict(values, SampleType=rich_type.UID())
    >>> rich_source = create_analysisrequest(client, request,
    ...     rich_values, [service.UID()])

    >>> rich_source.setCCEmails("alice@example.com,bob@example.com")
    >>> rich_source.setClientOrderNumber("ORD-12345")
    >>> rich_source.setClientReference("REF-XYZ")
    >>> rich_source.setEnvironmentalConditions("ambient, dry")
    >>> rich_source.setComposite(True)

Reference fields too. CCContact is a multi-valued UIDReferenceField
— a different code path inside `copy_field_values`:

    >>> contact2 = api.create(client, "Contact",
    ...     Firstname="Jane", Surname="Roe")
    >>> rich_source.setCCContact([contact2])

Profiles is a multi-valued UID reference of a different type:

    >>> profile = api.create(setup.analysisprofiles, "AnalysisProfile",
    ...     title="Quick")
    >>> profile.setServices([service.UID()])
    >>> rich_source.setProfiles([profile])

The duplicate inherits each value via `copy_field_values`:

    >>> rich_dup = create_duplicate_of(rich_source)
    >>> print(rich_dup.getCCEmails())
    alice@example.com, bob@example.com
    >>> print(rich_dup.getClientOrderNumber())
    ORD-12345
    >>> print(rich_dup.getClientReference())
    REF-XYZ
    >>> print(rich_dup.getEnvironmentalConditions())
    ambient, dry
    >>> rich_dup.getComposite()
    True

UID references resolve correctly (back to the same target objects):

    >>> [c.getId() for c in rich_dup.getCCContact()]
    ['contact-2']
    >>> [p.getId() for p in rich_dup.getProfiles()]
    ['analysisprofile-1']

The snapshot reflects exactly the same values. This is the
guarantee the `skip_snapshots` + post-copy `take_snapshot`
approach buys us — `copy_field_values` writes through field
setters and would not, on its own, cause an audit entry:

    >>> rich_snap = snap_api.get_snapshots(rich_dup)[0]
    >>> print(rich_snap["CCEmails"])
    alice@example.com, bob@example.com
    >>> print(rich_snap["ClientOrderNumber"])
    ORD-12345
    >>> print(rich_snap["ClientReference"])
    REF-XYZ
    >>> print(rich_snap["EnvironmentalConditions"])
    ambient, dry
    >>> bool(rich_snap.get("Composite"))
    True

UID-typed fields land in the snapshot too. Format depends on
SuperModel.to_dict() (UID string vs. dict summary), so we just
check that the source's target UID appears in the serialised value:

    >>> api.get_uid(contact2) in repr(rich_snap.get("CCContact"))
    True
    >>> api.get_uid(profile) in repr(rich_snap.get("Profiles"))
    True

Still exactly one snapshot, action 'create':

    >>> len(snap_api.get_snapshots(rich_dup))
    1
    >>> print(snap_api.get_snapshots(rich_dup)[0]["__metadata__"]["action"])
    create


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

The same outcome is achievable via the `duplicate_sample`
transition, which fires the `after_duplicate_sample` event:

    >>> succeeded, message = do_action_for(source, "duplicate_sample")
    >>> succeeded
    True


The source remains in its previous state after the transition
(``new_state`` is empty):

    >>> api.get_workflow_status_of(source)
    'sample_due'


Global toggle disables the transition
.....................................

The setup carries a ``sample_duplicate_enabled`` flag. When
disabled, the `duplicate_sample` guard returns False and the
transition is no longer offered:

    >>> senaite_setup = api.get_senaite_setup()
    >>> senaite_setup.getSampleDuplicateEnabled()
    True

    >>> senaite_setup.setSampleDuplicateEnabled(False)
    >>> tids = [t["id"] for t in api.get_transitions_for(source)]
    >>> "duplicate_sample" in tids
    False

    >>> succeeded, message = do_action_for(source, "duplicate_sample")
    >>> succeeded
    False

Re-enable for the remaining tests:

    >>> senaite_setup.setSampleDuplicateEnabled(True)
    >>> "duplicate_sample" in [t["id"] for t in api.get_transitions_for(source)]
    True


Duplicates honour a custom ID Server schema
...........................................

Duplicates do not use a dedicated ID template; they share the
`AnalysisRequest` ID format and counter. So when an integrator
customises the `AnalysisRequest` template through the ID Server
admin, duplicates render with the same shape as plain samples.

Use a fresh SampleType so the persistent counter for the new
template's storage key starts at 1:

    >>> soil_type = api.create(sampletypes, "SampleType",
    ...     Prefix="soil", MinimumVolume="100 ml")

Override the `AnalysisRequest` template:

    >>> senaite_setup = api.get_senaite_setup()
    >>> formatting = list(senaite_setup.getIDFormatting() or [])
    >>> for record in formatting:
    ...     if record.get("portal_type") == "AnalysisRequest":
    ...         record["form"] = "{sampleType}-{year}-{seq:03d}"
    >>> senaite_setup.setIDFormatting(formatting)

A new source sample of the fresh type gets the customised ID:

    >>> soil_values = dict(values, SampleType=soil_type.UID())
    >>> custom_source = create_analysisrequest(client, request,
    ...     soil_values, [service.UID()])
    >>> year = DateTime().strftime("%y")
    >>> api.get_id(custom_source) == "soil-{}-001".format(year)
    True

Duplicates of that source pick up the same template:

    >>> custom_dup = create_duplicate_of(custom_source)
    >>> api.get_id(custom_dup) == "soil-{}-002".format(year)
    True

    >>> IAnalysisRequestDuplicate.providedBy(custom_dup)
    True

    >>> custom_dup.getDuplicatedFrom() == custom_source
    True

Subsequent duplicates continue along the same counter:

    >>> custom_dup2 = create_duplicate_of(custom_source)
    >>> api.get_id(custom_dup2) == "soil-{}-003".format(year)
    True


Opt-in: dedicated ID template for duplicates
............................................

The ID Server natively recognises the `AnalysisRequestDuplicate`
portal type — same way it handles `AnalysisRequestPartition`,
`AnalysisRequestRetest` and `AnalysisRequestSecondary`. By default
no row exists for it in `id_formatting`, so duplicates fall through
to the regular `AnalysisRequest` template (and counter). To opt
into a dedicated template, just add a row in the ID Server admin.

Add the row:

    >>> formatting = list(senaite_setup.getIDFormatting() or [])
    >>> formatting.append({
    ...     "form": "{parent_ar_id}-D{duplicate_count:02d}",
    ...     "portal_type": "AnalysisRequestDuplicate",
    ...     "prefix": "analysisrequestduplicate",
    ...     "sequence_type": "generated",
    ...     "context": "",
    ...     "counter_type": "",
    ...     "counter_reference": "",
    ...     "split_length": 1,
    ... })
    >>> senaite_setup.setIDFormatting(formatting)

Create a fresh source so the per-source duplicate counter starts
at 1 (the previous custom_source already has two duplicates from
the section above):

    >>> air_type = api.create(sampletypes, "SampleType",
    ...     Prefix="air", MinimumVolume="100 ml")
    >>> air_values = dict(values, SampleType=air_type.UID())
    >>> opt_in_source = create_analysisrequest(client, request,
    ...     air_values, [service.UID()])
    >>> opt_in_source_id = api.get_id(opt_in_source)

A new duplicate now renders with the dedicated template,
incorporating the source's ID and a per-source counter:

    >>> opt_in_dup = create_duplicate_of(opt_in_source)
    >>> api.get_id(opt_in_dup) == "{}-D01".format(opt_in_source_id)
    True

A second opt-in duplicate increments the per-source counter:

    >>> opt_in_dup2 = create_duplicate_of(opt_in_source)
    >>> api.get_id(opt_in_dup2) == "{}-D02".format(opt_in_source_id)
    True

Plain sample creation still uses the regular AR template — the
duplicate template is only consulted when the marker is provided:

    >>> plain_after_optin = create_analysisrequest(client, request,
    ...     air_values, [service.UID()])
    >>> api.get_id(plain_after_optin).startswith("air-{}-".format(year))
    True
    >>> api.get_id(plain_after_optin).endswith("-D01")
    False
