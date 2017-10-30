The following are the rules to follow when adding new upgrade steps:

1) If the upgrade step is required by a contribution to be merged into master,
   increase the last number of the version.
   eg.: from v01_00_000.py to v01_00_001.py

2) If the upgrade step is required by a contribution that will be merged into
   develop branch (in most cases, big changes in code, architectural, etc.),
   increase the second number of the version.
   eg.: from v01_00_000.py to v01_01_000.py

Also remember to update the version number in bika/lims/profiles/metadata.xml
and bika/lims/upgrade/configure.zcml
