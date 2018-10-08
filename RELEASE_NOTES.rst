Release notes
=============

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

  - Reindex of getDueDate for Analyses
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
