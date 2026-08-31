# Client Role Mechanism

This package implements how a SENAITE user becomes a "client user" at
runtime: how the user is recognised, how the platform decides what they
are allowed to see, and how the catalog filters listings down to that
user's own data. It replaces an older persistent-group mechanism that
did not scale and accumulated state across the database.

The code lives in `clientrole.py`. The registration is in
`configure.zcml`. The matching catalog-side machinery sits in
`senaite.core.catalog.indexer.allowedrolesandusers` and
`senaite.core.catalog.base_catalog.BaseCatalog._listAllowedRolesAndUsers`.


## Background: the legacy mechanism

Up to SENAITE 2.6, granting a contact access to their client folder
worked like this:

1. When a Client was created, a per-client Plone group was
   auto-generated and the `Owner` local role was granted to that
   group on the Client folder.
2. Linking a Contact to a Plone user added the user to the
   per-client group. The group itself carried the global `Client`
   role.
3. Local-role acquisition propagated `Owner` from the Client folder
   to every descendant, so the user could see their samples, batches,
   reports, etc.
4. The catalog index `allowedRolesAndUsers` carried a
   `user:<group_id>` token on every descendant.

The mechanism worked but had three structural problems:

- **Catalog churn on every link.** Any change to local roles on a
  populated Client triggered a recursive `reindexObjectSecurity` over
  every descendant. On a Client with tens of thousands of samples
  this was visibly slow.
- **Leaky abstraction.** The group lived in the global `portal_groups`
  tool, was named after a hashed client id, and showed up in unrelated
  admin views.
- **Half-broken opt-out.** A registry flag was supposed to disable
  the auto-create behaviour, but several call sites bypassed the
  flag and lazy-created the group anyway.

The new mechanism keeps the user-visible effect (a linked Contact can
read their own client tree) but removes the per-client group and the
persisted local-role grant.


## The new mechanism in one paragraph

The user object carries a single member property,
`linked_client_uid`, holding the UID of the Client the user is bound
to (empty string if none). Direct traversal is authorised by a
dynamic `ILocalRoleProvider` registered for `IClient` and
`IClientAwareMixin`: it reads `linked_client_uid` and returns
`("Owner", "Client")` whenever the user's UID matches the client
that contains the adapted context. Catalog access is authorised by a
stable `client:<client_uid>` token added to `allowedRolesAndUsers`
during indexing; the catalog query injects the asking user's
`client:<linked_client_uid>` token via a `BaseCatalog` override.
The whole system is therefore stateless on the catalog side: linking
or unlinking a Contact writes a single property on a user, and no
catalog object ever needs to be reindexed because of it.


## The three role providers

`clientrole.py` registers three `ILocalRoleProvider` adapters.

### `ClientLinkRoleProvider` for `IClientAwareMixin`

Adapts every object on the client tree (Samples, Batches, Analyses,
Reports, Sample Points, …). On `getRoles(principal_id)` it walks the
context to its enclosing Client, compares the Client's UID to the
asking user's `linked_client_uid`, and returns `("Owner", "Client")`
on match.

`Owner` is the long-established broad-access role on the client
tree. `Client` is the SENAITE-specific role that enables several
per-field edit permissions on Sample (Date Sampled, Sample Type,
Client Order Number, …) and the `senaite.core: View Navigation`
permission. Granting both makes `Client` a dynamic, contextual role
that is never assigned globally.

`getAllRoles()` returns an empty iterator. This is intentional. The
catalog's `allowedRolesAndUsers` indexer enumerates principals via
`getAllRoles`. Enumerating every linked client user there would
re-introduce the catalog churn we just removed: every link/unlink
would force a reindex of every client-tree descendant. We refuse to
enumerate, and instead carry a stable `client:<uid>` token whose
value is bound to the client identity, not to the membership list.

### `ClientRoleProvider` for `IClient`

The Client folder itself does not provide `IClientAwareMixin` (it
provides `IClient`), so the provider above does not adapt it. This
subclass plugs the gap for the folder itself so the linked user has
`Owner + Client` on the Client folder root, not just on its
descendants.

### `GlobalClientRoleProvider` for `ISiteRoot`

Returns `("Client",)` to any user whose `linked_client_uid` is set,
regardless of context. The grant is recorded on the site root, so
local-role acquisition propagates it to every descendant.

This exists to satisfy permission checks that fire **above** the
client tree. The sidebar's `View Navigation` check, for example,
runs on the portal root or on `bika_setup`. The per-context
providers above only fire on the client tree, so without this third
provider client users would see "permission denied" on the sidebar
items even though their actual client-tree access is correct.

`getAllRoles` is again empty for the same reason.


## How the catalog stays consistent

The catalog index `allowedRolesAndUsers` is computed by an
`@indexer` factory registered on `IClient` and `IClientAwareMixin`.
The factory calls the standard Plone indexer to get the base tokens
(`user:<id>` from `__ac_local_roles__`, group tokens, role names),
then appends one extra token, `client:<client_uid>`, derived from
the enclosing Client.

`BaseCatalog._listAllowedRolesAndUsers` augments the asking user's
allowed-roles list at query time. Specifically, it appends
`client:<linked_client_uid>` if the user has the property set. The
result is symmetric with the indexer: a SENAITE Sample under
client X carries `client:X` in its index, and the catalog query for
a user linked to X injects the same `client:X`, so the brain
matches.

The token is bound to the client identity, not to the list of users
who currently have access. Linking or unlinking a Contact therefore
does not require a reindex.


## Security model invariants (what stops cross-client leakage)

The dynamic role mechanism above keeps a linked client contact out
of other clients' data through three layered defences. Each layer
is necessary; none of them is sufficient on its own. New code
touching the client tree must respect every one.

### Defence 1: identity-bound catalog token

Every client-tree brain carries a stable `client:<client_uid>`
token in its `allowedRolesAndUsers` index, and every SENAITE
catalog (subclasses of `BaseCatalog`) injects the asking user's
`client:<linked_client_uid>` token at query time. Brains and
queries match only when both UIDs are identical.

This is what protects **identity-scoped catalog listings** from
returning another client's content. It is independent of role
names and persistent local roles.

### Defence 2: per-view permission stricter than `View`

The `View` permission's role list in the portal rolemap includes
`Client`, and every linked client contact carries the global
`Client` role from `GlobalClientRoleProvider`. Local-role
acquisition propagates `Client` from the site root to every
descendant. Combined with `View acquired="True"` in most workflow
states, this means a linked client user technically has `View`
permission on every client-tree object in the portal, not just
their own.

The cross-client isolation on **direct URL access** therefore
relies on each `<browser:page>` registration declaring a
permission stricter than `View` — typically
`senaite.core.permissions.ManageAnalysisRequests`, which is only
granted to `Owner` (per-context, on the user's own client tree
via `ClientLinkRoleProvider`) and to lab roles.

> **Rule for new views on `IClient`, `IBatch`, `IAnalysisRequest`,
> `IAnalysis`, `IResultsReport`, `IAttachment` and any other
> client-tree type**: do not register them with
> `permission="zope2.View"` or `permission="cmf.View"`. Use a
> per-context permission such as
> `senaite.core.permissions.ManageAnalysisRequests` (read views)
> or `senaite.core.permissions.ModifyPortalContent` (edit views),
> both of which only grant to `Owner` + lab roles.

### Defence 3: query path-scoping

Listings that traverse the client subtree (e.g. the per-Client
`ReportsListingView`, the per-Batch `analysisrequests` view) add
an explicit `path` filter scoped to `api.get_path(self.context)`
to the catalog query. This is belt-and-suspenders next to
defence 1: even if a catalog bug skips the
`client:<uid>` injection one day, the path filter still constrains
the result set to the current container's subtree.

### Why all three defences together

The global `Client` role is the legacy compatibility shim that
makes the sidebar's `View Navigation` permission resolve for
client users. Removing it would break the UI. Replacing it with
a strictly per-context grant would force `getAllRoles` to
enumerate every linked user, which is the very catalog-reindex
storm #2934 was written to eliminate.

The cost of keeping the global `Client` grant is that **role
names alone cannot enforce cross-client isolation**. Defences 1
and 2 close that gap: defence 1 inside the catalog query, defence
2 at every direct-URL entry point.


## `IClientAwareMixin` notes

Two interfaces share the name `IClientAwareMixin`:

- `bika.lims.interfaces.IClientAwareMixin` is the AT-era marker.
  AT content (`Batch`, `AnalysisRequest`, `AbstractRoutineAnalysis`,
  `AnalysisSpec`, `ARTemplate`, `Attachment`, `ARReport`) declares it
  through `bika.lims.content.clientawaremixin.ClientAwareMixin`.

- `senaite.core.interfaces.IClientAwareMixin` is the DX marker.
  DX content (`SamplePoint`, `SampleType`, `AnalysisProfile`, …)
  declares it through `senaite.core.content.mixins.ClientAwareMixin`.

The two interface objects have byte-identical definitions but are
distinct: `IA.providedBy(obj)` returns `True` for `obj` only if `obj`
declares exactly `IA`, not a different interface with the same name.

The role provider, the catalog indexer, the v02_07_000 reindex
upgrade step, and `bika.lims.utils.get_client` therefore all import
`IClientAwareMixin` from `senaite.core.interfaces` (the DX symbol),
and the AT `ClientAwareMixin` base class also declares the DX marker
so AT content participates in the same machinery. The AT symbol is
kept declared for downstream consumers that still reference it; it
will be removed once external code migrates.


## Onboarding a linked Contact

When a contact is linked to a Plone user, the contact link/unlink
hooks write or clear the `linked_client_uid` member property on the
user object. The hooks live in `bika.lims.content.contact` and
`senaite.core.content.contact`.

No group is created. No `__ac_local_roles__` is written. No
descendant is reindexed.

The `linked_client_uid` property is itself persisted through the
mutable-properties plugin so it survives LDAP-only sessions and is
not dropped on logout. See PR #2939.


## Migration

The v02_07_000 series carries the following idempotent steps:

1. Reindex `allowedRolesAndUsers` on every `IClient`-providing or
   `IClientAwareMixin`-providing brain so each one picks up its
   `client:<uid>` token.
2. Backfill `linked_client_uid` on every user that is currently
   linked to a Contact under a Client.
3. Drop the orphan registry record for the now-removed
   `auto_create_client_group` setting.
4. Strip directly-assigned global `Client` roles (the role is now
   granted via the dynamic provider on the site root).
5. Remove the legacy per-client groups and the corresponding
   `Owner` entries from `__ac_local_roles__` on each Client folder.
6. Remove the `manage_access` action from the Client FTI (sharing
   on the client tree is disabled because access is dynamic).

Steps 1 and 2 are prerequisites: after they run, every user who was
linked under the old model continues to see their data under the new
model. Steps 5 and 6 remove the now-dead legacy state.


## Operational notes

- Listings that target SENAITE catalogs subclass `BaseCatalog` and
  therefore inherit the query-side injection automatically. No view
  has to opt in.

- Any external listing that bypasses SENAITE catalogs (raw
  `portal_catalog` queries with explicit `allowedRolesAndUsers`
  filtering) must inject `client:<linked_client_uid>` itself to
  show client data.

- The `@@sharing` view is disabled on the client tree. Granting
  ad-hoc local roles there would no longer be reflected in the
  catalog token (which is bound to client identity, not to the
  acl_users membership list).

- Bulk reindex operations should call `catalog.catalog_object(obj,
  idxs=["allowedRolesAndUsers"], update_metadata=False)` directly
  on each affected catalog and skip `obj.reindexObject`. The
  `CatalogMultiplexProcessor` queue otherwise dominates the wall
  clock for production-size datasets.


## Related interfaces and files

- `senaite.core.interfaces.IClientAwareMixin`
- `senaite.core.content.mixins.ClientAwareMixin`
- `bika.lims.interfaces.IClientAwareMixin`
- `bika.lims.content.clientawaremixin.ClientAwareMixin`
- `senaite.core.catalog.indexer.allowedrolesandusers`
- `senaite.core.catalog.base_catalog.BaseCatalog`
- `bika.lims.content.contact._linkUser` / `_unlinkUser`
- `senaite.core.content.contact._set_user_property`
- `senaite.core.upgrade.v02_07_000`
