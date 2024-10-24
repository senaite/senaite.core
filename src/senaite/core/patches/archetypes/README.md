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

Due to the fact that SENAITE catalogs inherit from
`Products.CMFPlone.CatalogTool.CatalogTool`, which is a subclass of
`Products.CMFCore.CatalogTool.CatalogTool`, this operation uses the `IndexQueue`
defined in `Products.CMFCore.indexing.IndexQueue` to optimize indexing.

### Notes

The index queue always looks up all registered `IIndexQueueProcessor` utilities
to further delegate the operation.

Since the `PortalCatalogProcessor` utility is registered there as well, a
patching is required to avoid indexing of, e.g. Samples or Analyses there as
they should be only indexed in their primary catalog, e.g.
`seanite_catalog_sample` or `senaite_catalog_analysis`.

Plase see `senaite.core.patches.cmfcore.portal_catalog_processor` for details.


## UID Catalog indexing

The module `referencable` contains patches for the class
`Products.Archetypes.Referencable.Referencable`, which is a mixin for
`BaseObject` and controls AT native referencable behavior (not used) and the
indexing in the UID Catalog (used and needed for UID references and more).

### Patches

The following methods are patched:

- `_catalogUID_`
- `uncatalogUID`

### Reason

The patches ensure that temporary objects are not indexed.

### Notes

As soon as we have migrated all contents to Dexterity, we should provide a
custom `senaite_catalog_uid` to keep track of the UIDs and maybe references.
