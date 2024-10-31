# CMFCore Patches

This package contains patches for `Products.CMFCore`.

## Portal Catalog Processor

The module `portal_catalog_processor` contains patches for the class
`Products.CMFCore.indexing.PortalCatalogProcessor` which is registered as the
default `IIndexQueueProcessor` utility for the `portal_catalog`.


### Patches

The following methods are patched:

- `index`
- `unindex`
- `reindex`

### Reason

The patches ensure that AT based SENAITE content types are not additionally
indexed in `portal_catalog` if they have a primary catalog assigned, e.g.
Samples -> `senaite_catalog_sample`.

### Notes

Currently, we only keep the root folders like `Clients`, `Methods`, `Samples` etc. in `portal_catalog`.


## Workflow Tool

The modules `workflowtool` contains patches for the class `Products.CMFCore.WorkflowTool.WorkflowTool`,
which provides workflow related methods like e.g. the `doActionFor` method to
transition from one workflow state to the other.

### Patches

The following methods are patched:

- `_reindexWorkflowVariables`

### Reason

Please see docstring and https://github.com/senaite/senaite.core/pull/2593 for details.

### Notes

Removing this patch made the test `WorkflowAnalysisUnassign` fail, which is an unexpected side-effect.

TODO: We need to investigate the reason of this behavior!
