Sample creation - Conflict retry
--------------------------------

The sample add form supports two creation strategies, selected by the
registry flag `sample_add_form_commit_per_sample`:

- **off (default)**: the whole batch is created in a single
  transaction; the existing all-or-nothing semantics apply.
- **on**: each sample is committed in its own transaction with a
  per-sample retry on `ZODB.POSException.ConflictError`, plus a
  second-pass retry at the end of the batch. Samples that ultimately
  fail are reported back to the user with their column index and any
  operator-supplied identifier.

This doctest exercises the retry path without requiring a real
multi-connection ZODB conflict, by stubbing `create_sample` on the
view to raise `ConflictError` on demand.

Test Setup
..........

Running this test from the buildout directory:

    bin/test -t SampleCreationConflictRetry

Needed Imports:

    >>> import transaction
    >>> from bika.lims import api
    >>> from bika.lims.browser.analysisrequest.add2 import \
    ...     ajaxAnalysisRequestAddView
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from senaite.core.interfaces import INumberGenerator
    >>> from senaite.core.registry import get_registry_record
    >>> from senaite.core.registry import set_registry_record
    >>> from zope.component import getUtility
    >>> from ZODB.POSException import ConflictError

Variables and a minimal client / sample type / service so the legacy
path has something real to commit when we invoke it:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bikasetup = portal.bika_setup
    >>> setRoles(portal, TEST_USER_ID, ['LabManager'])
    >>> client = api.create(portal.clients, "Client",
    ...     Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(client, "Contact",
    ...     Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType",
    ...     title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact",
    ...     Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department",
    ...     title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories,
    ...     "AnalysisCategory", title="Metals", Department=department)
    >>> Cu = api.create(bikasetup.bika_analysisservices,
    ...     "AnalysisService", title="Copper", Keyword="Cu",
    ...     Category=category.UID())

Instantiate the add view directly. We do not exercise the full submit
flow; we just need an object with the helper methods bound to a real
request:

    >>> view = ajaxAnalysisRequestAddView(portal, request)
    >>> view.MAX_CREATE_ATTEMPTS = 3

Identifier helpers
..................

`_record_identifier` falls back gracefully when the user did not type
any identifying field:

    >>> view._record_identifier({})
    u'-'
    >>> view._record_identifier({"ClientSampleID": "CSID-42"})
    u'CSID-42'
    >>> view._record_identifier({"ClientReference": "ref-9"})
    u'ref-9'

`ClientSampleID` takes precedence over `ClientReference`:

    >>> view._record_identifier({
    ...     "ClientSampleID": "CSID-1", "ClientReference": "ref-9"})
    u'CSID-1'

Toggle dispatch
...............

With the flag off (default) `create_samples` calls the legacy
single-transaction path; with it on, the per-commit path:

    >>> calls = []
    >>> view._create_samples_per_commit = lambda r: calls.append("commit") or []
    >>> view._create_samples_single_transaction = lambda r: calls.append("single") or []
    >>> _ = set_registry_record("sample_add_form_commit_per_sample", False)
    >>> view.create_samples([])
    []
    >>> calls[-1]
    'single'
    >>> _ = set_registry_record("sample_add_form_commit_per_sample", True)
    >>> view.create_samples([])
    []
    >>> calls[-1]
    'commit'

Retry succeeds after a transient conflict
.........................................

Replace `create_sample` with a stub that raises `ConflictError` on its
first invocation and returns a marker object on the second. The retry
loop must catch the conflict, sleep, and retry, ending with the
marker returned and the attempt counter at 2:

    >>> attempts = {"n": 0}
    >>> def flaky_create(client, record, attachments=None, source=None):
    ...     attempts["n"] += 1
    ...     if attempts["n"] < 2:
    ...         raise ConflictError("simulated counter contention")
    ...     return "sample-ok"
    >>> view.create_sample = flaky_create
    >>> view.MAX_CREATE_ATTEMPTS = 3

The retry helper bypasses the dispatch; we drive it directly so the
test does not depend on the full record-validation path. We also
abort any pending transaction first so the commit inside the helper
operates on a clean state:

    >>> transaction.abort()
    >>> user = api.user.get_user()
    >>> result = view._create_one_with_retry(
    ...     client, {"Client": client.UID()}, [], None,
    ...     user=user, path_info="/test")
    >>> result
    'sample-ok'
    >>> attempts["n"]
    2

Retry exhaustion reports the failure
....................................

Now make `create_sample` raise on every call. The helper must give up
after `MAX_CREATE_ATTEMPTS` and return `None`:

    >>> attempts = {"n": 0}
    >>> def always_conflict(client, record, attachments=None, source=None):
    ...     attempts["n"] += 1
    ...     raise ConflictError("permanent counter contention")
    >>> view.create_sample = always_conflict
    >>> transaction.abort()
    >>> result = view._create_one_with_retry(
    ...     client, {"Client": client.UID()}, [], None,
    ...     user=user, path_info="/test")
    >>> result is None
    True
    >>> attempts["n"] == view.MAX_CREATE_ATTEMPTS
    True

`_report_failed_records` surfaces each failed row with its column
index and identifier in a single portal message:

    >>> view._report_failed_records([
    ...     (2, {"ClientSampleID": "CSID-A12"}),
    ...     (5, {"ClientReference": "ref-9"}),
    ...     (7, {}),
    ... ])
    >>> messages = portal.plone_utils.showPortalMessages(request)
    >>> [m.message for m in messages if "could not be created" in m.message][-1]
    u'Could not create the following sample(s) due to transaction conflicts, please retry them: #2 (CSID-A12), #5 (ref-9), #7 (-)'

Numbers are not burned on retry
...............................

The ID-counter contention this feature targets is harmless to
sequence integrity: when a transaction that has bumped the counter
aborts, the storage write is discarded with it, so the next caller
reads the original value. We verify the property directly against
`INumberGenerator`:

    >>> ng = getUtility(INumberGenerator)
    >>> key = "test-conflict-retry"
    >>> _ = ng.set_number(key, 100)
    >>> ng.get(key)
    100

Bump the counter inside a transaction, then abort it; the storage
sees the original value again on the next read:

    >>> transaction.begin()
    <...>
    >>> _ = ng.generate_number(key=key)
    >>> ng.get(key) >= 101
    True
    >>> transaction.abort()
    >>> ng.get(key)
    100

The next successful generation produces 101, not a value past the
aborted attempt:

    >>> transaction.begin()
    <...>
    >>> ng.generate_number(key=key)
    101
    >>> transaction.commit()

Reset the registry flag so other tests are not affected:

    >>> _ = set_registry_record("sample_add_form_commit_per_sample", False)
