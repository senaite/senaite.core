# Concept: Sample Clone

Implementation plan for a new `clone_to_new` transition that produces a
copy of an existing sample whose analyses preserve their per-instance
configuration but start with empty result fields.

## Motivation

Establishing method repeatability requires running the same sample
multiple times on the same detector, often ten or more iterations. The
existing "Copy" action creates a new sample but reinstantiates analyses
from the AnalysisService defaults, losing per-instance overrides such
as Calculation, Method, Instrument, and InterimFields configuration.

A Clone action keeps the original analyses' setup so each clone is a
ready-to-measure replica, while clearing the previous results so each
clone records an independent measurement.

Original ticket:
https://github.com/ridingbytes/iaea.lims/issues/271

## Behavior

- Single click on a Clone button creates exactly one clone, similar to
  iaea.lims' Dilute action.
- The clone uses the next standard sample ID, no special suffix.
- The clone inherits Client, SampleType, Batch, and all schema fields
  from the source.
- Each cloned analysis preserves its source analysis' Calculation,
  Method, Instrument, Specification, Unit, and InterimFields config,
  with InterimFields values reset to their defaults.
- The clone's analyses start with no Result, Uncertainty,
  ResultCaptureDate, or Analyst.
- The clone has a `ClonedFrom` backlink to the source. No status
  message viewlet for now.
- The source sample remains in its current workflow state. The clone
  enters the workflow at `sample_received` (or whichever the standard
  default is for newly created samples).

## Implementation

### 1. New schema field on AnalysisRequest

File: `bika/lims/content/analysisrequest.py`

Add a `ClonedFrom` field next to `DetachedFrom`:

```python
UIDReferenceField(
    "ClonedFrom",
    allowed_types=("AnalysisRequest",),
    relationship="AnalysisRequestClonedFrom",
    mode="rw",
    read_permission=View,
    write_permission=ModifyPortalContent,
    widget=ReferenceWidget(
        label=_(
            "label_sample_cloned_from",
            default="Cloned from"),
        description=_(
            "description_sample_cloned_from",
            default="Reference to the source sample this sample was "
                    "cloned from"),
        render_own_label=True,
        readonly=True,
        visible=False,
        catalog_name=SAMPLE_CATALOG,
    ),
),
```

The `relationship` value enables backref tracking via
`get_backreferences`, useful later for surfacing clones on the source.

### 2. Clone factory

File: `bika/lims/utils/analysisrequest.py`

Add `create_clone_of(sample)`:

```python
CLONE_SKIP_FIELDS = [
    "Analyses",
    "Attachment",
    "ClonedFrom",
    "DetachedFrom",
    "DatePublished",
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
    "modification_date",
    "id",
]

CLONE_RESET_ANALYSIS_FIELDS = [
    "Result",
    "Uncertainty",
    "ResultCaptureDate",
    "Analyst",
]


def create_clone_of(sample):
    """Create a clone of the given sample.

    The clone preserves all schema fields of the source as well as the
    per-instance configuration of each analysis (Calculation, Method,
    Instrument, Specification, Unit, InterimFields config). Results
    and result-related fields are reset on the cloned analyses.
    """
    ar = api.get_object(sample)

    # Build the field record from the source
    record = fields_to_dict(ar, CLONE_SKIP_FIELDS)
    record["ClonedFrom"] = api.get_uid(ar)

    # Collect source analyses and their services
    source_analyses = ar.getAnalyses(full_objects=True)
    services = list({api.get_uid(a.getAnalysisService())
                     for a in source_analyses})

    # Preserve results ranges
    results_ranges = ar.getResultsRange() or []

    # Create the clone
    client = ar.getClient()
    clone = create_analysisrequest(
        client,
        request=api.get_request(),
        values=record,
        analyses=services,
        results_ranges=results_ranges,
    )

    # Apply per-instance overrides on each cloned analysis
    src_by_keyword = {a.getKeyword(): a for a in source_analyses}
    for cloned_analysis in clone.getAnalyses(full_objects=True):
        kw = cloned_analysis.getKeyword()
        src = src_by_keyword.get(kw)
        if src is None:
            continue
        copy_analysis_config(src, cloned_analysis)

    return clone


def copy_analysis_config(source, target):
    """Copy per-instance config from source analysis to target.

    Resets InterimFields values to their defaults and leaves Result,
    Uncertainty, ResultCaptureDate, and Analyst untouched on target.
    """
    target.setCalculation(source.getCalculation())
    target.setMethod(source.getMethod())
    target.setInstrument(source.getInstrument())
    if hasattr(target, "setSpecification"):
        target.setSpecification(source.getSpecification())
    if hasattr(target, "setUnit"):
        target.setUnit(source.getUnit())

    interims = []
    for interim in source.getInterimFields():
        item = dict(interim)
        item["value"] = item.get("default", "")
        interims.append(item)
    target.setInterimFields(interims)
```

### 3. Workflow guard

File: `bika/lims/workflow/analysisrequest/guards.py`

```python
def guard_clone_to_new(analysis_request):
    """Always allow cloning a sample"""
    return True
```

### 4. Workflow event handler

File: `bika/lims/workflow/analysisrequest/events.py`

```python
def after_clone_to_new(analysis_request):
    """Create a clone after the clone_to_new transition is performed.

    The transition runs on the source sample. It does not change the
    source's state; the after-event creates a sibling clone.
    """
    clone = create_clone_of(analysis_request)
    clone.reindexObject()
```

### 5. Workflow definition

File: `senaite/core/profiles/default/workflows/senaite_sample_workflow/definition.xml`

Register the `clone_to_new` transition:

- `new_state` empty so the source's state is unchanged.
- `trigger` is USER.
- Permission `senaite.core: Transition: Clone to New` (define a new
  permission, similar to `senaite.core: Transition: Copy to New`).
- Available from every state in which Copy to New is available, at
  minimum: `sample_due`, `sample_received`, `to_be_verified`,
  `verified`, `published`.

The transition guard expression points to
`guard_handler/clone_to_new`.

### 6. Permission definition

File: `senaite/core/permissions/sample/permissions.py`

```python
TransitionCloneToNew = "senaite.core: Transition: Clone to New"
```

Register in the rolemap (`rolemap.xml`) of the default profile so
`LabManager`, `Manager`, and `LabClerk` can use it (mirror the rights
of `TransitionCopyToNew`).

### 7. Workflow action adapter

File: `bika/lims/browser/workflow/analysisrequest.py`

```python
class WorkflowActionCloneToNewAdapter(WorkflowActionGenericAdapter):
    """Adapter in charge of the 'clone_to_new' action"""

    def __call__(self, action, objects):
        transitioned = self.do_action(action, objects)
        if not transitioned:
            return self.redirect(message=_("No clone created"),
                                 level="warning")
        clones = [o.getBackReferences("AnalysisRequestClonedFrom")
                  for o in transitioned]
        clones = [c for sub in clones for c in sub]
        ids = ", ".join(map(api.get_id, clones))
        message = _("Cloned items: {}").format(ids)
        return self.success(transitioned, message=message)
```

The adapter triggers the transition (which fires `after_clone_to_new`),
then reports the new clone ID(s) in a status message.

### 8. ZCML registration

File: `bika/lims/browser/workflow/configure.zcml`

```xml
<adapter
    name="workflow_action_clone_to_new"
    for="* zope.publisher.interfaces.browser.IBrowserRequest"
    factory=".analysisrequest.WorkflowActionCloneToNewAdapter"
    provides="bika.lims.interfaces.IWorkflowActionAdapter" />
```

### 9. Translations

Update the `senaite.core` `.po` files with:

- `label_sample_cloned_from`
- `description_sample_cloned_from`
- The transition label "Clone" used by the workflow definition.

### 10. Upgrade step

Bump `metadata.xml` and add an upgrade step in
`senaite/core/upgrade/v02_07_000.py` (or the next minor) that:

- Re-imports the workflow profile so the new transition is registered
  on existing samples.
- Re-imports the rolemap so the new permission is granted.

### 11. Tests

Add `senaite/core/tests/doctests/SampleClone.rst` covering:

- Cloning a basic sample creates a sibling with `ClonedFrom` set.
- Per-instance overrides on analyses are preserved on the clone.
- InterimFields config is preserved while interim values reset to
  defaults.
- Result and Uncertainty are empty on cloned analyses.
- Source sample's state is unchanged after cloning.

### 12. Changelog

Add an entry to `CHANGES.rst` under the next unreleased section:

```
- #XXXX Add clone_to_new transition for samples
```

## Out of scope for the first iteration

- No batch cloning ("clone N times" input). One click yields one clone.
  Repeat the action to get more.
- No backref viewlet on the source sample showing its clones. The
  `ClonedFrom` field is queryable for later UI work.
- No special handling of partitions: cloning a primary clones only
  that sample's analyses, not the partition tree. A future iteration
  may extend the existing `AfterCreateSampleHook` to copy partitions
  for clones in the same way it does for `copy_to_new`.

## Open questions

- Should the clone be allowed when the source has invalidated
  retracted analyses? Likely yes, since the clone starts fresh.
- Should `ResultsRange` overrides be carried via the
  `results_ranges` argument or re-applied per analysis after creation?
  The proposed implementation uses `results_ranges` at creation time;
  worth verifying it covers all cases.
- Should the cloned analyses inherit the source's worksheet
  assignment? Default behavior of `create_analysisrequest` is no, and
  that matches the repeatability use case (each clone is independent).
