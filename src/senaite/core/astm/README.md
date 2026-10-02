# SENAITE ASTM Interface

This package receives instrument results from the
[senaite.astm](https://github.com/senaite/senaite.astm) middleware and
imports them into SENAITE.

The middleware listens on TCP for lab instruments (ASTM frames or HL7 v2
over MLLP), parses every session into a JSON envelope, and POSTs it to
SENAITE's `@@API/senaite/v1/push` endpoint. This package is the
consumer of that envelope.


## Envelope format

The current contract is the **2.x envelope**: one top-level dict with a
`metadata` block and per-record-type buckets, every bucket a list of
dicts.

    {
        "metadata": {
            "envelope_version": "1.1",
            "astm":   "<raw ASTM frames>",
            "lis2a":  "<raw LIS2-A payload>",
            "hl7":    "<raw HL7 v2 payload>"
        },
        "H": [{...}],    # Header
        "P": [{...}],    # Patient
        "O": [{...}],    # Order
        "R": [{...}, ...],   # Result
        "C": [{...}, ...],   # Comment
        "M": [{...}, ...],   # Manufacturer info
        "L": [{...}],    # Terminator
        "Q": [{...}, ...]    # Request information
    }

The bucket layout is transport-agnostic — both ASTM records and HL7
segments are routed into the same H/P/O/R/C buckets so a downstream
importer can stay transport-blind. For HL7 the per-record fields are
keyed by stringified field number, e.g. `envelope["R"][0]["3"]` is
`OBX-3`; for ASTM the keys match the Python record-class attribute
names like `result_name`, `sender`, `sample_id`.

`senaite.astm` 1.x produced a looser shape: no `metadata` block, no HL7
buckets, and `H[0]["sender"]` could be either a dict (`{"name": ...,
"serial": ...}`) or a list (`[name, serial, version]`). The consumer
accepts both shapes.


## Dispatch

The push consumer is registered for the name `senaite.core.lis2a.import`
(both 1.x and 2.x middleware default to that consumer name when
`--message-format json` is set).

For every envelope in the batch, the consumer:

1. Extracts the sender name from `H[0].sender` (handles both the dict
   and list shape).
2. Looks up an `IASTMImporter` *named* adapter for that sender. If none
   is registered, falls back to the generic unnamed adapter.
3. Calls `importer.import_data()`.

That means a customer project registers one adapter per instrument
model:

```xml
<configure xmlns="http://namespaces.zope.org/zope">
    <adapter name="HemoScreen"
             factory=".astm_importer.ASTMImporter" />
</configure>
```

The adapter name must equal the `H[0].sender.name` the instrument
sends.


## Writing an importer

Subclass `senaite.core.astm.importer.ASTMImporter` and implement
`import_data`. The base class provides:

- `self.data` — the parsed envelope.
- `self.message` — the raw JSON string (use this when storing the
  payload as an attachment).
- `self.instrument` — best-matching Instrument from the SENAITE setup,
  resolved by sender name + serial; logs ambiguous matches.
- `self.sample` — Sample resolved from the order's sample ID; falls
  back to `getClientSampleID` only when it has a single hit, and logs
  ambiguous fallbacks.
- `self.get_header()`, `self.get_order()`, `self.get_results()`,
  `self.get_patients()`, `self.get_comments()` — bucket accessors.
- `self.get_sender()` — `(name, serial, version)` tuple from the
  header.
- `self.log(...)` — appends to an `AutoImportLog` content item
  attached to the instrument; created lazily on first call.
- `self.create_attachment(container, contents, filename)` — write the
  raw payload as an `Attachment` on the sample's client.

Minimal example:

```python
from bika.lims import api
from senaite.core.astm.importer import ASTMImporter as Base
from senaite.core.interfaces import IASTMImporter, ISenaiteCore
from zope.component import adapter
from zope.interface import Interface, implementer

ALLOWED_SAMPLE_STATES = ["sample_received"]


@adapter(Interface, Interface, ISenaiteCore)
@implementer(IASTMImporter)
class ASTMImporter(Base):
    """ASTM results importer for the Horiba Yumizen H5xx."""

    def import_data(self):
        if not self.instrument:
            return self.log("Instrument not found")
        if not self.sample:
            return self.log("Sample not found")

        state = api.get_workflow_status_of(self.sample)
        if state not in ALLOWED_SAMPLE_STATES:
            return self.log(
                "Sample state must be in %s" % ALLOWED_SAMPLE_STATES)

        sender = self.get_sender()
        filename = "%s.txt" % "_".join(sender)
        self.create_attachment(
            self.sample.getClient(), self.message, filename=filename)

        for result in self.get_results():
            # … set the value on the matching analysis …
            pass
```


## Server configuration

Point `senaite-astm-server` (or `senaite-hl7-server` from 2.x) at this
SENAITE instance with `--message-format json`:

    $ senaite-astm-server \
        -m json \
        -c senaite.core.lis2a.import \
        -u http://admin:admin@localhost:8080/senaite

See `senaite-astm-server --help` and `senaite-hl7-server --help` for
the full option list.


## Roadmap

The current pattern asks every customer to write a per-instrument
adapter. Most adapters do the same six things — extract the sample
ID, extract the analysis keyword and normalise it, read value /
status / flag / timestamp, optionally filter (e.g. HemoScreen
`OBR-4 = OBS` only), and write the result through a shared helper.
A generic profile-driven importer reading YAML or content-type
definitions is in the works; see the sketch at
`sketches/senaite-astm-generic-importer/` in the buildout repo.
