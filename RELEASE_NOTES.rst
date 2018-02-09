Release notes
=============

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
