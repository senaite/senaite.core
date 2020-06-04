API Snapshot
============

The snapshot API provides a simple interface to manage object snaphots.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t API_snapshot


Test Setup
----------

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.api.snapshot import *
    >>> from bika.lims.permissions import FieldEditAnalysisHidden
    >>> from bika.lims.permissions import FieldEditAnalysisResult
    >>> from bika.lims.permissions import FieldEditAnalysisRemarks
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD

Functional Helpers:

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def new_sample(services):
    ...     values = {
    ...         "Client": client.UID(),
    ...         "Contact": contact.UID(),
    ...         "DateSampled": date_now,
    ...         "SampleType": sampletype.UID()}
    ...     service_uids = map(api.get_uid, services)
    ...     return create_analysisrequest(client, request, values, service_uids)

    >>> def get_analysis(sample, id):
    ...     ans = sample.getAnalyses(getId=id, full_objects=True)
    ...     if len(ans) != 1:
    ...         return None
    ...     return ans[0]


Environment Setup
-----------------

Setup the testing environment:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.bika_setup
    >>> date_now = DateTime().strftime("%Y-%m-%d")
    >>> date_future = (DateTime() + 5).strftime("%Y-%m-%d")
    >>> setRoles(portal, TEST_USER_ID, ['LabManager', ])
    >>> user = api.get_current_user()


LIMS Setup
----------

Setup the Lab for testing:

    >>> setup.setSelfVerificationEnabled(True)
    >>> analysisservices = setup.bika_analysisservices
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> labcontact = api.create(setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.bika_departments, "Department", title="Chemistry", Manager=labcontact)
    >>> sampletype = api.create(setup.bika_sampletypes, "SampleType", title="Water", Prefix="Water")


Content Setup
-------------

Create some Analysis Services with unique Keywords:

    >>> Ca = api.create(analysisservices, "AnalysisService", title="Calcium", Keyword="Ca")
    >>> Mg = api.create(analysisservices, "AnalysisService", title="Magnesium", Keyword="Mg")
    >>> Cu = api.create(analysisservices, "AnalysisService", title="Copper", Keyword="Cu")
    >>> Fe = api.create(analysisservices, "AnalysisService", title="Iron", Keyword="Fe")
    >>> Au = api.create(analysisservices, "AnalysisService", title="Aurum", Keyword="Au")
    >>> Test1 = api.create(analysisservices, "AnalysisService", title="Calculated Test Service 1", Keyword="Test1")
    >>> Test2 = api.create(analysisservices, "AnalysisService", title="Calculated Test Service 2", Keyword="Test2")

Create an new Sample:

    >>> sample = new_sample([Cu, Fe, Au])

Get the contained `Cu` Analysis:

    >>> cu = get_analysis(sample, Cu.getKeyword())
    >>> fe = get_analysis(sample, Fe.getKeyword())
    >>> au = get_analysis(sample, Au.getKeyword())


Check if an object supports snapshots
-------------------------------------

We can use the `support_snapshots` function to check if the object supports
snapshots:

    >>> supports_snapshots(sample)
    True

    >>> supports_snapshots(object())
    False


Get the snapshot storage
------------------------

The snapshot storage holds all the raw snapshots in JSON format:

    >>> storage = get_storage(sample)
    >>> storage
    ['{...}']


Get all snapshots
-----------------

To get the data snapshots of an object, we can call `get_snapshots`:

    >>> snapshots = get_snapshots(sample)
    >>> snapshots
    [{...}]


Check if an object has snapshots
--------------------------------

To check if an object has snapshots, we can call `has_snapshots`:

    >>> has_snapshots(sample)
    True

    >>> has_snapshots(cu)
    True

    >>> has_snapshots(fe)
    True

    >>> has_snapshots(au)
    True

    >>> has_snapshots(setup)
    False


Get the number of snapshots
---------------------------

To check the number of snapshots (versions) an object has, we can call
`get_snapshot_count`:

    >>> get_snapshot_count(sample)
    2

    >>> get_snapshot_count(setup)
    0


Get the version of an object
----------------------------

If an object has a snapshot, it is considered as version 0:

    >>> get_version(cu)
    0

If the object does not have any snapshots yet, this function returns -1:

    >>> get_version(object())
    -1


Get a snapshot by version
-------------------------

Snapshots can be retrieved by their index in the snapshot storage (version):

    >>> get_snapshot_by_version(sample, 0)
    {...}

Negative versions return `None`:

    >>> get_snapshot_by_version(sample, -1)

Non existing versions return `None`:

    >>> get_snapshot_by_version(sample, 9999)


Get the version of a snapshot
-----------------------------

The index (version) of each snapshot can be retrieved:

    >>> snap1 = get_snapshot_by_version(sample, 0)
    >>> get_snapshot_version(sample, snap1)
    0

    >>> snap2 = get_snapshot_by_version(sample, 1)
    >>> get_snapshot_version(sample, snap2)
    1


Get the last snapshot taken
---------------------------

To get the latest snapshot, we can call `get_last_snapshot`:

   >>> snap = get_last_snapshot(sample)
   >>> get_snapshot_version(sample, snap)
   1


Get the metadata of a snapshot
------------------------------

Each snapshot contains metadata which can be retrieved:

   >>> metadata = get_snapshot_metadata(snap)
   >>> metadata
   {...}

The metadata holds the information about the performing user etc.:

   >>> metadata.get("actor")
   u'test_user_1_'

   >>> metadata.get("roles")
   [u'Authenticated', u'LabManager']


Take a new Snapshot
-------------------

Snapshots can be taken programatically with the function `take_snapshot`:

    >>> get_version(sample)
    1

Now we take a new snapshot:

    >>> snapshot = take_snapshot(sample)

The version should be increased:

    >>> get_version(sample)
    2

The new snapshot should be the most recent snapshot now:

    >>> last_snapshot = get_last_snapshot(sample)

    >>> last_snapshot == snapshot
    True


Comparing Snapshots
-------------------

The changes of two snapshots can be compared with `compare_snapshots`:

   >>> snap0 = get_snapshot_by_version(sample, 2)

Add 2 more analyses (Mg and Ca):

   >>> sample.edit(Analyses=[Cu, Fe, Au, Mg, Ca])
   >>> new_snapshot = take_snapshot(sample)
   >>> snap1 = get_snapshot_by_version(sample, 3)

Passing the `raw=True` keyword returns the raw field changes, e.g. in this case,
the field `Analyses` is a `UIDReferenceField` which contained initially 3 values
and after adding 2 analyses, 2 UID more references:

   >>> diff_raw = compare_snapshots(snap0, snap1, raw=True)
   >>> diff_raw
   {u'Analyses': [([u'...', u'...', u'...'], [u'...', u'...', u'...', u'...', u'...'])]}

It is also possible to process the values to get a more human readable diff:

   >>> diff = compare_snapshots(snap0, snap1, raw=False)
   >>> diff
   {u'Analyses': [('Aurum; Copper; Iron', 'Aurum; Calcium; Copper; Iron; Magnesium')]}


To directly compare the last two snapshots taken, we can call
`compare_last_two_snapshots`.

First we edit the sample to get a new snapshot:

   >>> sample.edit(CCEmails="rb@ridingbytes.com")
   >>> snapshot = take_snapshot(sample)

   >>> last_diff = compare_last_two_snapshots(sample, raw=False)
   >>> last_diff
   {u'CCEmails': [('Not set', 'rb@ridingbytes.com')]}
