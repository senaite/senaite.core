# P8: Plone 5 + Python 3 Upgrade Guide

This document is inteded to give a rough plan how to achieve an upgrade of
[SENAITE][SE] to the latest [Plone 5][P5] codebase in combination with Python 3.
Therfore, it is named *P8*.


## Why Python 3?

The current codebase of [SENAITE][SE] is only compatible with Plone 4 and Python
2.x. Python stops support for the 2.x series by January 2020.


## How to achieve it?

SENAITE needs to be first compatible with Plone 5 in combination with Python 2.
It need then to be checked if the [Archetypes framework][AT] is compatible with
Python 3 or not.

It need then to be considered to migrate existing content types to the new
[Dexterity][DX] or stick to [Archetypes][AT] and try to make this framework
compatible to Python 3.

Especially the compatibility with customer addons and the migration of all the
Archetypes based fields need to be considered in this step.


## Roadmap

This roadmap outlines the most important steps of the upgrade process in a
logical order:

1. Accomplish to upgrade to Plone 5
2. Make the codebase Python 2/3 compatible with [six][SX]
3. Upgrade non-complex content types to [Dexterity][DX], e.g. controlpanel
   folders
4. Upgrade JavaScript libraries, especially compatibility with the latest
   [jQuery][JQ] library
4. Upgrade Archetypes fields to [z3c.form][ZF] fields
5. Upgrade non-complex fields to [Dexterity][DX]
6. Upgrade to Python 3


## Python 2/3 compatibility

This section lists the most importatnt snippets how to use the [six][SX] library
already today in the [SENAITE][SE] codebase to prepare the code for Python 3
compatibility.

This section is inteded to grow on the way


### Check if the object is a string

https://six.readthedocs.io/#six.string_types

Before:

    if isinstance(thing, basestring):
        ...

After:

    import six

    if isinstance(thing, six.string_types):
        ...
        
        
## Support

Migrating the [SENAITE][SE] Project to Plone 5 and Python 3 is a huge effort and
cannot be achieved without the support of the community. 

Please consider therefore to support us to keep SENAITE an open-source success
story: https://community.senaite.org/t/how-can-senaite-be-maintained-open-source


## Companies behind SENAITE

- NARALABS: https://naralabs.com
- RIDING BYTES: https://www.ridingbytes.com


[P5]: https://github.com/plone/Products.CMFPlone  "Plone 5"
[SE]: https://github.com/senaite/senaite.core  "SENAITE Core"
[AT]: https://github.com/plone/Products.Archetypes  "Plone Archetypes Framework"
[SX]: https://six.readthedocs.io  "Python 2 and 3 Compatibility Library"
[DX]: https://docs.plone.org/develop/plone/content/dexterity.html  "Dexterity"
[JQ]: https://jquery.com "jQuery"
[ZF]: https://docs.plone.org/develop/plone/forms/z3c.form.html  "z3c.form library"
