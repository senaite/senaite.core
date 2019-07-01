Release notes
=============

Update from 1.3.0 to 1.3.1
--------------------------

**IMPORTANT: Plan the upgrade with enough time**

This update might take long depending on the number of objects registered in
the system:

- Stale Sample and Partition objects have been removed from ZODB
  https://github.com/senaite/senaite.core/pull/1351

- Full Audit log has been added to Senaite
  https://github.com/senaite/senaite.core/pull/1324

If you have your own add-on, please review the changes to check beforehand
if some parts of your add-on require modifications. Worth to mention that the
following tips are strongly recommended before proceeding with the upgrade:

- Do a zeopack
- Do a backup of both your code and database
- Try to have as much analyses in verified/published statuses as possible
- Stop unnecessary applications and services that may consume RAM
- Start with a clean log file


Update from 1.2.9 to 1.3.0
--------------------------

**IMPORTANT: Plan the upgrade with enough time**

Version 1.3.0 is not a hotfix release, it rather comes with a lot of changes
that require additional care when planning the update. If you have your own
add-on, please review the changes to check beforehand if some parts of your
add-on require modifications.

This update will take long (up to 5h for instances with large amounts of data).
Therefore, is recommended to plan and allocate enough resources for the process
to complete beforehand. For big databases, RAM is a critical factor to be
considered before upgrading. Worth to mention that the following tips are
strongly recommended before proceeding with the upgrade:

- Do a zeopack
- Do a backup of both your code and database
- Try to have as much analyses in verified/published statuses as possible
- Stop unnecessary applications and services that may consume RAM
- Start with a clean log file

Most of the base code has been refactored keeping in mind the following
objectives:

- Less complexity: less code, better code
- High test coverage: lower chance of undetected bugs
- Boost performance: better experience, with no delays
- Improve security: rely on Zope's security policies
- Code responsibility: focus on core functionalities and let other add-ons to
  deal with the rest (`senaite.lims`, `senaite.core.listing`, etc.)

Besides of this refactoring, this version also comes with a myriad of new
functionalities and enhancements: full-fledged sample partitions, reinvented
listings and results entry, new adapters for extensibility, etc.

Version 1.3 is the result of hard, but exciting work at same time. Four months
of walking through valleys of tears and fighting hydras. Four exciting months to
be proud of.


Update from 1.2.8 to 1.2.9
--------------------------

**IMPORTANT: Plan the upgrade with enough time**
This update might take long depending on the number of Analyses, Analysis
Requests and Samples registered in the system:

- Role mappings updated for Analaysis Requests and Samples (rejection)
  https://github.com/senaite/senaite.core/pull/1041

- Recatalog of invalidated/retest Analysis Requests (invalidation)
  https://github.com/senaite/senaite.core/pull/1027

- Reindex and recatalog of getDueDate for Analysis Requests
  https://github.com/senaite/senaite.core/pull/1051

- Reindex of getDueDate for Analyses:
  https://github.com/senaite/senaite.core/pull/1032

- Workflow: `retract_ar` transition has been renamed to `invalidate`
  https://github.com/senaite/senaite.core/pull/1027


Update from 1.2.7 to 1.2.8
--------------------------

- Operators for min and max values have been added. For specifications already
  present in the system, the result ranges are considered as bounded and closed:
  `[min,max] = {result | min <= result <= max}`.
  https://github.com/senaite/senaite.core/pull/965


Update from 1.2.4 to 1.2.5
--------------------------

- This update requires the execution of `bin/buildout`, because
  Products.TextIndexNG3 has been added. It will help to search by wildcards in
  TextIndexNG3 indexes instead of looking for the keyword inside wildcards.
  For now, it is used only in AR listing catalog.
  https://pypi.python.org/pypi/Products.TextIndexNG3/

- This update might take long depending on the number of Analyses registered in
  the system, because the upgrade step will walk through all analyses in order
  to update those that do not have a valid (non-floatable) duplicate variation
  value (see #768).


Update from 1.2.3 to 1.2.4
--------------------------

- This update requires the execution of `bin/buildout`, because WeasyPrint has
  been updated to version 0.42.2:
  http://weasyprint.readthedocs.io/en/stable/changelog.html#version-0-42-2


Update from 1.2.2 to 1.2.3
--------------------------

- IMPORTANT: Plan the upgrade with enough time
  This update might take long depending on the number of Analysis Requests
  registered in the system because a new index and column 'assigned_state' has
  been added in Analysis Requests catalog, that require the catalog to be
  reindexed (see #637).


Update from 1.2.1 to 1.2.2
--------------------------

- IMPORTANT: Plan the upgrade with enough time
  This update might take long depending on the number of Batches registered in
  the system, because an index from their catalog needs to be reindexed (#574).
  Also, a new index that affects the Worksheets that have a Worksheet Template
  assigned has been added and needs to be indexed.


Update from 1.2.0 to 1.2.1
--------------------------

- This update requires the execution of `bin/buildout`, because a new dependency has
  been added: `Plone Subrequest <https://pypi.python.org/pypi/plone.subrequest/>`_

- With this update, Analyses Services that are inactive, but have active
  dependent services, will be automatically transitioned to `active` state. This
  procedure fixes eventual inconsistencies amongst the statuses of Analyses
  Services. See #555
