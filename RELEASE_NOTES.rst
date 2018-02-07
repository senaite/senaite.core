Release notes
=============

Update from 1.2.1 to 1.2.2
--------------------------

- Plan the upgrade with enough time.
  This update might take long depending on the number of Analysis Requests
  registered in the system because a new index and column 'assigned_state' has
  been added in Analysis Requests catalog, that require the catalog to be
  reindexed. See #637


Update from 1.2.0 to 1.2.1
--------------------------

- This update requires the execution of `bin/buildout`, because a new dependency has
  been added: `Plone Subrequest <https://pypi.python.org/pypi/plone.subrequest/>`_

- With this update, Analyses Services that are inactive, but have active
  dependent services, will be automatically transitioned to `active` state. This
  procedure fixes eventual inconsistencies amongst the statuses of Analyses
  Services. See #555
