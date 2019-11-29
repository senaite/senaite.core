# Code conventions

This guide explains the code conventions used in `senaite.core`, but extends to
any add-ons for `senaite` too.

## Catalogs

### Indexes naming

Names for catalog indexes don't follow the `CamelCase` naming convention, rather
all in lowercase and words separated by `_`:

- Bad: `getSampleTypeUID`
- Good: `sampletype_uid`

#### Plural and singular forms

Indexes will be written in singular form. There are a few exceptions, mostly
those that come from `Plone` or `Zope` (e.g. `allowedRolesAndUsers`). Quite
frequently, the plural form is used wrongly because the name of the meta-type
index to use leads us to think about the plural form: e.g. `KeywordIndex`, that
indexes a sequence of keywords. Is better to think about how the searches
against the index work.

For instance, for a given object, a `KeywordIndex` will store a sequence of
keywords, but if we do a search for single or multiple keywords against this
index, the search will only return those items that have at least one of the
keywords. And if there are multiple keyword matches for same item, the system
will only return the item once. Since we can query for any index (`FieldIndex`,
`KeywordIndex`, etc.) using a list, it does not make sense to use the plural
form. In fact, if you are forced to add an index in plural form because a given
index with same name, but in singular already exists, probably the index in
singular is a `FieldIndex`, that don't allow you to store multiple values. In
such case, the best approach is to change the meta-type of the existing index
from `FieldIndex` to `KeywordIndex`.

- Bad: `sampletype_titles`
- Good: `sampletype_title`


### Metadata fields naming

Metadata fields use the `get` prefix and eventually might follow the `CamelCase`
naming convention. The reason is that, at present time, SENAITE still uses 
Archetypes, and `ATContentType`'s mutators for Schema fields follow this naming
convention. Since one would expect the name of the metadata field to match
with the name of the function from the object, we keep same convention. This
might change in future when we move to `Dexterity`.

- Bad: `SampleTypeUID`
- Good: `getSampleTypeUID`

#### Plural and singular forms

For metadata fields, use plural forms when the field returns a list and use
singular when the field returns a single value.
