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
multi-connection ZODB conflict. We stub both the view's `create_sample`
(to raise `ConflictError` on demand) and the `transaction` module
operations the retry helper drives, so the test-layer transaction is
not disturbed.

Test Setup
..........

Running this test from the buildout directory:

    bin/test -t SampleCreationConflictRetry

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.browser.analysisrequest import add2
    >>> from bika.lims.browser.analysisrequest.add2 import \
    ...     ajaxAnalysisRequestAddView
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from senaite.core.registry import set_registry_record
    >>> from ZODB.POSException import ConflictError

Variables and a minimal LabManager role so the view has a sensible
context to bind to:

    >>> portal = self.portal
    >>> request = self.request
    >>> setRoles(portal, TEST_USER_ID, ['LabManager'])
    >>> view = ajaxAnalysisRequestAddView(portal, request)
    >>> original_max_attempts = add2.MAX_CREATE_ATTEMPTS
    >>> add2.MAX_CREATE_ATTEMPTS = 3

Stub out the `transaction` module binding on the `add2` module so the
retry helper does not commit or abort the layer's transaction. The
fake module mirrors the four entry points the helper uses; the
underlying `transaction` global stays untouched, so other tests are
not affected.

    >>> class TStub(object):
    ...     def setUser(self, *a, **kw): pass
    ...     def note(self, *a, **kw): pass
    >>> class FakeTransactionModule(object):
    ...     _t = TStub()
    ...     def begin(self): return self._t
    ...     def commit(self): return None
    ...     def abort(self): return None
    ...     def get(self): return self._t
    >>> original_txn_module = add2.transaction
    >>> add2.transaction = FakeTransactionModule()

Avoid real time.sleep in the retry backoff so the test runs fast.
Replace the `time` binding on the `add2` module rather than the
global `time` module:

    >>> class FakeTimeModule(object):
    ...     def sleep(self, *a, **kw): pass
    >>> original_time_module = add2.time
    >>> add2.time = FakeTimeModule()

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
    >>> _ = view.create_samples([])
    >>> calls[-1]
    'single'
    >>> _ = set_registry_record("sample_add_form_commit_per_sample", True)
    >>> _ = view.create_samples([])
    >>> calls[-1]
    'commit'

Retry succeeds after a transient conflict
.........................................

Replace `create_sample` with a stub that raises `ConflictError` on its
first invocation and returns a marker on the second. The retry helper
must catch the conflict and retry, ending with the marker returned and
the attempt counter at 2:

    >>> attempts = {"n": 0}
    >>> def flaky_create(client, record, attachments=None, source=None):
    ...     attempts["n"] += 1
    ...     if attempts["n"] < 2:
    ...         raise ConflictError("simulated counter contention")
    ...     return "sample-ok"
    >>> view.create_sample = flaky_create
    >>> user = api.user.get_user()
    >>> result = view._create_one_with_retry(
    ...     None, {"ClientSampleID": "X"}, [], None,
    ...     user=user, path_info="/test")
    >>> result
    'sample-ok'
    >>> attempts["n"]
    2

Retry exhaustion returns None
.............................

Now make `create_sample` raise on every call. The helper must give up
after `MAX_CREATE_ATTEMPTS` and return `None`:

    >>> attempts = {"n": 0}
    >>> def always_conflict(client, record, attachments=None, source=None):
    ...     attempts["n"] += 1
    ...     raise ConflictError("permanent counter contention")
    >>> view.create_sample = always_conflict
    >>> result = view._create_one_with_retry(
    ...     None, {"ClientSampleID": "X"}, [], None,
    ...     user=user, path_info="/test")
    >>> result is None
    True
    >>> attempts["n"] == add2.MAX_CREATE_ATTEMPTS
    True

Failed-record reporting
.......................

`_report_failed_records` builds a single portal message listing each
failed row by its column index and identifier. The message is a
`zope.i18nmessageid.Message`, so the row data lives in its `mapping`
attribute rather than the default string. We capture the call by
stubbing the plone utility on the view's context:

    >>> captured = []
    >>> class PUStub(object):
    ...     def addPortalMessage(self, msg, level):
    ...         captured.append((msg, level))
    >>> view.context = type("Ctx", (), {"plone_utils": PUStub()})()
    >>> view._report_failed_records([
    ...     (2, {"ClientSampleID": "CSID-A12"}),
    ...     (5, {"ClientReference": "ref-9"}),
    ...     (7, {}),
    ... ])
    >>> msg, level = captured[-1]
    >>> level
    'warning'
    >>> msg.mapping["rows"]
    u'#2 (CSID-A12), #5 (ref-9), #7 (-)'

In-flight cache is gated on publisher retries
.............................................

The in-flight cache short-circuits sample creation when the same
fingerprint has already been registered. It must only do so when the
current request is a publisher-level retry of the originating
submission. On a fresh first attempt two independent submissions with
identical bodies (same client, same defaults, no operator-supplied
identifier) hash to the same fingerprint, and treating that as a hit
would return the previously created samples instead of creating a
new one — surfacing to the operator as a "successfully created"
banner for a sample that was never written.

`_is_publisher_retry` consults Zope's `retry_count` attribute, which
is 0 on the first attempt and incremented on every re-publish:

    >>> add2._is_publisher_retry(request)
    False
    >>> request.retry_count = 1
    >>> add2._is_publisher_retry(request)
    True
    >>> request.retry_count = 0

A request that has no `retry_count` attribute at all (non-HTTP
requests, test layers, ...) is treated as a fresh first attempt:

    >>> class BareRequest(object):
    ...     pass
    >>> add2._is_publisher_retry(BareRequest())
    False

Fingerprint is scoped to the worker thread
..........................................

`_submission_fingerprint` mixes the current worker thread id into
the hash. Zope publisher retries re-publish on the same worker, so
the retry sees the same fingerprint as the original attempt and
recovers the in-flight UIDs as expected. Two concurrent submissions
with byte-identical bodies on *different* workers (e.g. an operator
hitting Submit across several browser tabs in quick succession)
produce different fingerprints and therefore cannot overwrite each
other's in-flight cache entries.

The fingerprint must start with the current thread's identifier:

    >>> import threading
    >>> fp = add2._submission_fingerprint(request)
    >>> tid = str(threading.current_thread().ident)
    >>> fp.startswith(tid + ":")
    True

A second call on the same thread with the same body returns the
same fingerprint (publisher retries are idempotent on the same
worker):

    >>> add2._submission_fingerprint(request) == fp
    True

Cleanup
.......

Restore the patched transaction operations, sleep, registry flag,
and in-flight cache so later tests run in a pristine environment:

    >>> request.retry_count = 0
    >>> add2._inflight.clear()
    >>> add2.transaction = original_txn_module
    >>> add2.time = original_time_module
    >>> add2.MAX_CREATE_ATTEMPTS = original_max_attempts
    >>> _ = set_registry_record("sample_add_form_commit_per_sample", False)
