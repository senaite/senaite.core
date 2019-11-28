# Code conventions

This guide explains the code conventions used in `senaite.core`, but extends to
any add-ons for `senaite` too.

## Catalogs

### Indexes naming

Names for catalog indexes don't follow the `CamelCase` naming convention, rather
all in lowercase and words separated by `_`:

- Wrong: `getSampleTypeUID`
- Good: `sampletype_uids`

### Metadata fields naming

Metadata fields use the `get` prefix and eventually might follow the `CamelCase`
naming convention. The reason is that, at present time, SENAITE still uses 
Archetypes, and `ATContentType`'s mutators for Schema fields follow this naming
convention. Since one would expect the name of the metadata field to match
with the name of the function from the object, we keep same convention. This
might change in future when we move to `Dexterity`.

- Wrong: `SampleTypeUID`
- Good: `getSampleTypeUID`

