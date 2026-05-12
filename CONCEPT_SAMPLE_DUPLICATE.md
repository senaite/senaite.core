# Concept: Sample Duplicate

Implementation plan for a new `duplicate` workflow transition on
samples (AnalysisRequest). It produces a direct copy of the source
sample without showing the `ar_add` form. The duplicate uses the
regular Sample ID format and counter; type distinction comes from
the `IAnalysisRequestDuplicate` marker interface and the
`DuplicatedFrom` lineage reference.

## Motivation

The existing "Copy to new" action redirects to `ar_add` pre-populated
with the source sample's values, requiring the user to confirm the
form. For repeat measurements on the same detector or for routine
"do this sample again" operations, the form roundtrip is friction.

A single-click action that creates a sibling copy directly removes
that friction while keeping full lineage queryable through the
`DuplicatedFrom` backref.

Original ticket:
https://github.com/ridingbytes/iaea.lims/issues/271

## Behavior

- Single click on a Duplicate action creates exactly one duplicate
  per selected source sample. No add form, no intermediate page.
- The duplicate inherits all schema fields from the source (Client,
  SampleType, Batch, Contacts, dates, etc.), exactly as the existing
  primary->secondary path does for shared metadata.
- Each analysis on the duplicate is created from the source's
  AnalysisService set, with the same field-copy behavior the
  Copy-to-new path uses (the helpers in
  `bika.lims.utils.analysisrequest` invoked from `ar_add`). No
  per-instance override logic is added on top: whatever Copy-to-new
  preserves today, Duplicate preserves identically.
- The duplicate's analyses start with no Result, Uncertainty,
  ResultCaptureDate, or Analyst.
- The duplicate gets a fresh Sample ID from the regular
  AnalysisRequest counter (e.g. `water-0042` -> `water-0043`), the
  same format Copy-to-new produces. No dedicated ID template, no
  setup option.
- Type distinction is provided by the `IAnalysisRequestDuplicate`
  marker interface plus the `DuplicatedFrom` UID reference back to
  the source. Listings, reports and queries can identify duplicates
  via either signal.
- No status-message viewlet for duplicates in this iteration.
- The source sample remains in its current workflow state. The
  duplicate enters the workflow at the standard initial state for
  newly created samples.
- The action is implemented as a workflow transition so it appears
  in the standard workflow menu and inherits the full permission /
  guard / event mechanics.
- Sample-structure copying (partitions) follows the same registry
  toggle as Copy-to-new: the existing
  `sample_add_form_copy_partitions` setting decides whether the
  source's partition structure is replicated on the duplicate. No
  new toggle is introduced.

## Implementation

### 1. Marker interface

File: `bika/lims/interfaces/__init__.py` (alongside
`IAnalysisRequestSecondary`)

```python
class IAnalysisRequestDuplicate(Interface):
    """Marker for samples created via the 'duplicate' transition"""
```

The marker is applied to the new sample inside the duplicate
factory. The portal type stays `AnalysisRequest`, so the ID server
uses the regular sample template; the marker is only used for type
distinction in listings, queries, and adapters.

### 2. Schema field on AnalysisRequest

File: `bika/lims/content/analysisrequest.py`

Add a `DuplicatedFrom` reference next to existing back-references
like `PrimaryAnalysisRequest` and `Invalidated`:

```python
UIDReferenceField(
    "DuplicatedFrom",
    allowed_types=("AnalysisRequest",),
    relationship="AnalysisRequestDuplicatedFrom",
    mode="rw",
    read_permission=View,
    write_permission=ModifyPortalContent,
    widget=ReferenceWidget(
        label=_(
            "label_sample_duplicated_from",
            default="Duplicated from"),
        description=_(
            "description_sample_duplicated_from",
            default="Reference to the source sample this sample "
                    "was duplicated from"),
        render_own_label=True,
        readonly=True,
        visible=False,
        catalog_name=SAMPLE_CATALOG,
    ),
),
```

The `relationship` value enables backref tracking via
`get_backreferences`, useful for surfacing duplicates on the source
sample later.

### 3. Duplicate factory

File: `bika/lims/utils/analysisrequest.py`

Add `create_duplicate_of(sample)`. The implementation reuses the
field-copy machinery already used by Copy-to-new, applied directly
without the form roundtrip:

```python
DUPLICATE_SKIP_FIELDS = [
    "Analyses",
    "Attachment",
    "DatePublished",
    "DetachedFrom",
    "DuplicatedFrom",
    "Invalidated",
    "ParentAnalysisRequest",
    "PrimaryAnalysisRequest",
    "Profiles",
    "RejectionReasons",
    "Remarks",
    "ResultsInterpretation",
    "ResultsInterpretationDepts",
    "Sample",
    "Template",
    "creation_date",
    "id",
    "modification_date",
]


def create_duplicate_of(sample):
    """Create a duplicate of the given sample.

    The duplicate inherits all schema fields of the source. Its
    analyses are recreated from the source's AnalysisService set,
    with empty results. The duplicate is marked as
    AnalysisRequestDuplicate so the ID server picks the
    duplicate-specific ID template.
    """
    ar = api.get_object(sample)

    record = fields_to_dict(ar, DUPLICATE_SKIP_FIELDS)
    record["DuplicatedFrom"] = api.get_uid(ar)

    services = list({api.get_uid(a.getAnalysisService())
                     for a in ar.getAnalyses(full_objects=True)})
    results_ranges = ar.getResultsRange() or []

    client = ar.getClient()
    duplicate = create_analysisrequest(
        client,
        request=api.get_request(),
        values=record,
        analyses=services,
        results_ranges=results_ranges,
    )
    alsoProvides(duplicate, IAnalysisRequestDuplicate)

    return duplicate
```

Note: the duplicate gets a regular Sample ID (no dedicated ID
template). The `IAnalysisRequestDuplicate` marker is applied for
type distinction only — it does not affect ID generation.

Structure copying (partitions) is delegated to the existing
`IAfterCreateSampleHook` (`senaite.core.subscribers.sample`). That
hook already reads the registry flag
`sample_add_form_copy_partitions` and replicates the source's
partition tree on the new sample when the source is passed in.
`create_duplicate_of` must therefore invoke the hook with
`source=ar` (the same way the Copy-to-new path does), so the
duplicate inherits structure under the same toggle as Copy-to-new
without any new registry setting.

### 4. ID server

No changes. The duplicate uses its real portal type
(`AnalysisRequest`) for ID generation, so it picks the standard
sample template (`{sampleType}-{seq:04d}`). It shares the regular
sample counter, which guarantees uniqueness without any extra
collision-handling logic.

### 5. Workflow transition

File: `senaite/core/profiles/default/workflows/senaite_sample_workflow/definition.xml`

Register a `duplicate` transition on the sample workflow:

- `new_state` empty — the source's state is unchanged.
- `trigger` USER.
- Permission `senaite.core: Transition: Duplicate Sample` (new).
- Available from exactly the same set of states as `copy_to_new`.
  The transition definition in
  `senaite_sample_workflow/definition.xml` should mirror
  `copy_to_new`'s `available_states` (or its equivalent guard
  expression) verbatim, so the two actions stay in lock-step on
  every state where Copy-to-new is currently exposed (and on every
  future state added to that list).
- Guard expression: `python: here.guard_handler('duplicate')`,
  resolving to `guard_duplicate(analysis_request)`.

### 6. Workflow guard

File: `bika/lims/workflow/analysisrequest/guards.py`

```python
def guard_duplicate(analysis_request):
    """Allow duplicating a sample.

    Always returns True for now. May later forbid duplicating
    invalidated or detached samples.
    """
    return True
```

### 7. Workflow event handler

File: `bika/lims/workflow/analysisrequest/events.py`

```python
def after_duplicate(analysis_request):
    """Create the duplicate sibling after the 'duplicate' transition
    fires on the source. The transition itself does not change the
    source's state.
    """
    duplicate = create_duplicate_of(analysis_request)
    duplicate.reindexObject()
```

### 8. Permission definition

File: `senaite/core/permissions/sample/permissions.py`

```python
TransitionDuplicateSample = "senaite.core: Transition: Duplicate Sample"
```

Register in `rolemap.xml` of the default profile so `LabManager`,
`Manager`, and `LabClerk` may use it (mirroring the rights of
`TransitionCopyToNew`).

### 9. Workflow action adapter

File: `bika/lims/browser/workflow/analysisrequest.py`

```python
class WorkflowActionDuplicateAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of the 'duplicate' action"""

    def __call__(self, action, objects):
        transitioned = self.do_action(action, objects)
        if not transitioned:
            return self.redirect(message=_("No duplicate created"),
                                 level="warning")
        backref = "AnalysisRequestDuplicatedFrom"
        duplicates = []
        for source in transitioned:
            duplicates.extend(source.getBackReferences(backref))
        ids = ", ".join(map(api.get_id, duplicates))
        message = _("Duplicated samples: {}").format(ids)
        return self.success(transitioned, message=message)
```

The adapter triggers the transition (which fires `after_duplicate`),
then reports the new IDs in a status message. There is no redirect
to `ar_add`.

### 10. ZCML registration

File: `bika/lims/browser/workflow/configure.zcml`

```xml
<adapter
    name="workflow_action_duplicate"
    for="* zope.publisher.interfaces.browser.IBrowserRequest"
    factory=".analysisrequest.WorkflowActionDuplicateAdapter"
    provides="bika.lims.interfaces.IWorkflowActionAdapter" />
```

### 11. Translations

Update the senaite.core PO files (EN + DE) with:

- `label_sample_duplicated_from`
- `description_sample_duplicated_from`
- The transition label "Duplicate" used by the workflow definition.
- The status messages emitted by the adapter.

### 12. Upgrade step

Bump `metadata.xml` (newest entry on top in ZCML) and add an upgrade
step in `senaite/core/upgrade/v02_07_000.py` (or the next minor) that:

- Re-imports the workflow profile so the new transition is
  registered on existing samples.
- Re-imports the rolemap so the new permission is granted.

### 13. Tests

Add `senaite/core/tests/doctests/SampleDuplicate.rst` covering:

- Duplicating a sample creates a sibling marked with
  `IAnalysisRequestDuplicate`, with `DuplicatedFrom` set.
- The duplicate's ID is the next free Sample ID from the regular
  AnalysisRequest counter (e.g. source `water-0001` -> duplicate
  `water-0002`).
- The duplicate inherits Client, SampleType, Batch, Contacts.
- The duplicate's analyses are created with empty Result /
  Uncertainty / ResultCaptureDate / Analyst.
- The source sample's state is unchanged after the transition.
- A user without `TransitionDuplicateSample` cannot trigger the
  action.
- With `sample_add_form_copy_partitions = True`, duplicating a
  sample with partitions creates an equivalent partition tree on
  the duplicate (delegated to `IAfterCreateSampleHook`).
- With `sample_add_form_copy_partitions = False`, the duplicate has
  no partitions even when the source does.

### 14. Changelog

Add an entry to `CHANGES.rst` under the next unreleased section:

```
- #XXXX Add 'duplicate' workflow transition for samples
```

### 15. Twitter-together announcement

Add `tweets/YYYY-MM-DD-PR<n>.tweet` for the senaite.core PR
announcing the new transition.

## Out of scope for the first iteration

- No batch UI ("duplicate N times" prompt). One click yields one
  duplicate per selected source. Re-run the action for more.
- No backref viewlet on the source listing its duplicates. The
  `DuplicatedFrom` field is queryable for later UI work.

## Resolved questions

- **Where is Duplicate available?** Same state set as `copy_to_new`,
  by reusing its `available_states` / guard expression. Includes
  partitions and secondaries, since Copy-to-new exposes them today.
- **What does the duplicate inherit?** Same as Copy-to-new. The
  factory reuses the `bika.lims.utils.analysisrequest` helpers
  invoked from `ar_add`, so no behavioral divergence is introduced.
- **ID format.** Duplicates use the regular Sample ID format
  (`{sampleType}-{seq:04d}`), shared with plain samples. No
  dedicated template, no setup option, no collision handling
  needed — the regular AR counter guarantees uniqueness. Type
  distinction is achieved via the `IAnalysisRequestDuplicate`
  marker and `DuplicatedFrom` reference, both of which are
  queryable for listings and reports.
