Re-register missing Dexterity FTI utilities
-------------------------------------------

A Dexterity content type is usable by ``createContent`` only when its
local ``IDexterityFTI`` utility is registered in the site's component
registry. That registration is performed by
``plone.dexterity.fti.register``, which is triggered by the
``ObjectAddedEvent`` fired when an FTI is *created* in ``portal_types``.

GenericSetup's ``typeinfo`` import only creates -- and therefore only
registers -- an FTI that does not yet exist. Re-importing a type that
already exists updates it in place without firing that event, so an FTI
left behind by a partially-completed upgrade keeps a valid
``portal_types`` entry but loses its local utility, and content creation
raises ``ComponentLookupError``.

``senaite.core.upgrade.utils.register_missing_dx_ftis`` reconciles that
state by (re)registering the utility for any Dexterity FTI that is
missing it.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t UpgradeDexterityFTIRegistration


Test Setup
..........

Needed imports:

    >>> from plone.dexterity.interfaces import IDexterityFTI
    >>> from plone.dexterity.utils import createContent
    >>> from senaite.core.upgrade.utils import register_missing_dx_ftis
    >>> from zope.component import ComponentLookupError
    >>> from zope.component import getSiteManager
    >>> from zope.component import queryUtility

Variables:

    >>> portal = self.portal

We use ``Samples``, a Dexterity type installed with senaite.core, as the
subject throughout this test:

    >>> portal_type = "Samples"

Its FTI object is present in ``portal_types`` ...

    >>> fti = portal.portal_types.getTypeInfo(portal_type)
    >>> IDexterityFTI.providedBy(fti)
    True

... and its local utility is registered, so content can be created:

    >>> queryUtility(IDexterityFTI, name=portal_type) is not None
    True

    >>> createContent(portal_type) is not None
    True


Simulate a partially-migrated FTI
.................................

Unregister the local utility to reproduce the state left behind by an
interrupted migration: the FTI object stays in ``portal_types`` but the
utility is gone.

    >>> sm = getSiteManager()
    >>> sm.unregisterUtility(provided=IDexterityFTI, name=portal_type)
    True

    >>> queryUtility(IDexterityFTI, name=portal_type) is None
    True

Now content creation fails, even though the FTI object still exists:

    >>> fti = portal.portal_types.getTypeInfo(portal_type)
    >>> IDexterityFTI.providedBy(fti)
    True

    >>> try:
    ...     createContent(portal_type)
    ...     print("No error raised")
    ... except ComponentLookupError:
    ...     print("ComponentLookupError raised")
    ComponentLookupError raised


Reconcile the registrations
...........................

``register_missing_dx_ftis`` re-registers the missing utility:

    >>> register_missing_dx_ftis()

    >>> queryUtility(IDexterityFTI, name=portal_type) is not None
    True

Content can be created again:

    >>> createContent(portal_type) is not None
    True

The helper is idempotent: running it again when nothing is missing
leaves the existing registration untouched:

    >>> util = queryUtility(IDexterityFTI, name=portal_type)
    >>> register_missing_dx_ftis()
    >>> queryUtility(IDexterityFTI, name=portal_type) is util
    True
