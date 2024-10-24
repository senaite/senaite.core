# Archetypes Patches

This package contains patches for Archetype based content types.

## Catalog Multiplex

The module `catalog_multiplex` contains patches for the class
`Products.Archetpyes.CatalogMultiplex.CatalogMultiplex`, which is a mixin for
`BaseContent` and controls how to index, unindex, reindex these content and is
used when e.g. `obj.reindexObject` is called.

### Patches

The following methods are patched:

- `indexObject`
- `unindexObject`
- `reindexObject`

### Reason

The patches ensure that temporary objects are not indexed and delegate the
operation to the respective method of the catalog itself.

Due to the fact that SENAITE catalogs inherit from `Products.CMFPlone.CatalogTool.CatalogTool`,
which is a subclass of `Products.CMFCore.CatalogTool.CatalogTool`, this operation uses the
`IndexQueue` defined in `Products.CMFCore.indexing.IndexQueue` to optimize indexing.

### Notes

The index queue always looks up all registered `IIndexQueueProcessor` utilities
to further delegate the operation.

Since the `PortalCatalogProcessor` utility is registered there as well, a
patching is required to avoid indexing of, e.g. Samples or Analyses there as
they should be only indexed in their primary catalog, e.g.
`seanite_catalog_sample` or `senaite_catalog_analysis`.

Please see `senaite.core.patches.cmfcore.portal_catalog_processor` for details.

Furthermore, changes in `senaite.core.catalog.catalog_multiplex_processor.CatalogMultiplexProcessor` 
were required to handle AT based contens as well.

Please see https://github.com/senaite/senaite.core/pull/2632 for details.

💡 It might make sense to define for each catalog its own `IIndexQueueProcessor`.
A simple check by content type would could decide if a content should be indexed or not.


## UID Catalog indexing

The module `referencable` contains patches for the class `Products.Archetypes.Referencable.Referencable`,
which is a mixin for `BaseObject` and controls AT native referencable behavior
(not used) and the indexing in the UID Catalog (used and needed for UID
references and more).

### Patches

The following methods are patched:

- `_catalogUID_`
- `uncatalogUID`

### Reason

The patches ensure that temporary objects are not indexed.

### Notes

As soon as we have migrated all contents to Dexterity, we should provide a
custom `senaite_catalog_uid` to keep track of the UIDs and maybe references.


## Base Object

The module `base_objects` contains patches for the class `Products.Archetypes.BaseObject.BaseObject`,
which is the base class for our AT based contents.

### Patches

The following methods are patched:

- `getLabels`
- `isTemporary`

### Reason

Provide a similar methods for AT contents as for DX contents.

**getLabels**: Get SENAITE labels (dynamically extended fields)

**isTemporary**: Checks if an object contains a temporary ID to avoid further indexing/processing
