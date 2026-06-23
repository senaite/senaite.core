API remarks
-----------

The remarks API (`senaite.core.api.remarks`) provides shared helpers for the
Remarks field, used by both the Archetypes and the Dexterity field
implementations as well as the widget endpoints.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t API_remarks


Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from senaite.core.api import remarks
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bika_setup = portal.bika_setup

Assume the role of Lab Manager:

    >>> setRoles(portal, TEST_USER_ID, ["Manager"])


Sanitizing and converting content
.................................

`to_safe_html` sanitizes content through the `text/x-html-safe` transform::

    >>> "<script>" in remarks.to_safe_html("<script>alert(1)</script>ok")
    False

`to_plain_text` converts (safe) HTML back to plain text, unescaping entities
and preserving line breaks::

    >>> remarks.to_plain_text("<p>Bitte z&uuml;gig bearbeiten</p>")
    u'Bitte z\xfcgig bearbeiten'
    >>> remarks.to_plain_text("<p>line one</p><p>line two</p>")
    u'line one\nline two'
    >>> remarks.to_plain_text("one<br/>two")
    u'one\ntwo'
    >>> remarks.to_plain_text("")
    ''


Creating and editing records
............................

`make_record` creates a new remark record with the full shape::

    >>> record = remarks.make_record("Hello world", user_id="bob")
    >>> sorted(record.keys())
    ['content', 'created', 'deleted', 'deleted_by', 'id', 'modified', 'modified_by', 'user_id', 'user_name', 'versions']
    >>> record["user_id"]
    'bob'
    >>> record["modified"]
    ''
    >>> record["versions"]
    []

`apply_edit` updates the content and keeps the prior content as a version::

    >>> created = record["created"]
    >>> updated = remarks.apply_edit(record, "Hello there", editor_id="alice")
    >>> "Hello there" in updated["content"]
    True
    >>> updated["modified_by"]
    'alice'
    >>> updated["modified"] != ""
    True
    >>> len(updated["versions"])
    1
    >>> "Hello world" in updated["versions"][0]["content"]
    True

The original creation date is preserved::

    >>> updated["created"] == created
    True

`apply_delete` soft-deletes the record, stamping who deleted it and when::

    >>> deleted = remarks.apply_delete(record, user_id="carol")
    >>> deleted["deleted_by"]
    'carol'
    >>> deleted["deleted"] != ""
    True


Finding records
...............

`find_record` returns the (index, record) tuple by id, or (None, None)::

    >>> records = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    >>> remarks.find_record(records, "b")
    (1, {'id': 'b'})
    >>> remarks.find_record(records, "x")
    (None, None)


User helpers
............

`get_user_fullname` falls back to the user id when no full name is available::

    >>> remarks.get_user_fullname("nonexistent-user")
    'nonexistent-user'


Resolving the field
...................

Create a Sample that holds a Remarks field::

    >>> clients = portal.clients
    >>> client = api.create(clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(client, "Contact", Firstname="Rita", Surname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", Prefix="water", MinimumVolume="100 ml")
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Water")
    >>> service = api.create(bika_setup.bika_analysisservices, "AnalysisService", title="pH", Keyword="PH", Category=category)
    >>> values = {
    ...     "Client": client.UID(),
    ...     "Contact": contact.UID(),
    ...     "DateSampled": DateTime().strftime("%Y-%m-%d"),
    ...     "SampleType": sampletype.UID(),
    ... }
    >>> sample = create_analysisrequest(client, request, values, [service.UID()])

`get_remarks_field` resolves the field by name and rejects other fields::

    >>> field = remarks.get_remarks_field(sample, "Remarks")
    >>> field is not None
    True
    >>> remarks.get_field_name(field)
    'Remarks'
    >>> remarks.get_remarks_field(sample, "Title") is None
    True
    >>> remarks.get_remarks_field(sample, "NonExistent") is None
    True

`get_records` returns the field records as plain dicts::

    >>> new_record = field.add(sample, "First remark")
    >>> records = remarks.get_records(sample, field)
    >>> len(records)
    1
    >>> isinstance(records[0], dict)
    True


Permissions
...........

A manager can view, add and manage remarks::

    >>> remarks.can_view_remarks(sample)
    True
    >>> remarks.can_add_remark(sample)
    True
    >>> remarks.can_manage_remarks(sample)
    True

An anonymous user can neither view nor add remarks::

    >>> from plone.app.testing import logout
    >>> logout()
    >>> remarks.can_view_remarks(sample)
    False
    >>> remarks.can_add_remark(sample)
    False

    >>> from plone.app.testing import login
    >>> from plone.app.testing import TEST_USER_NAME
    >>> login(portal, TEST_USER_NAME)

Editing is restricted to the author: a manager may not edit a remark authored
by somebody else (the manager override is deletion, not editing)::

    >>> current = api.get_current_user().id
    >>> remarks.can_edit_record(sample, {"user_id": "somebody-else"})
    False
    >>> remarks.can_edit_record(sample, {"user_id": current})
    True

A manager may delete any remark (the manager override)::

    >>> remarks.can_delete_record(sample, {"user_id": "somebody-else"})
    True

A non-manager may neither edit somebody else's remark nor delete::

    >>> setRoles(portal, TEST_USER_ID, ["Owner"])
    >>> remarks.can_manage_remarks(sample)
    False
    >>> remarks.can_edit_record(sample, {"user_id": "somebody-else"})
    False
    >>> remarks.can_delete_record(sample, {"user_id": "somebody-else"})
    False
    >>> setRoles(portal, TEST_USER_ID, ["Manager"])

Deleted remarks can no longer be edited or deleted again::

    >>> remarks.can_edit_record(sample, {"user_id": current, "deleted": "x"})
    False
    >>> remarks.can_delete_record(sample, {"deleted": "x"})
    False


Localization
............

`localize_record` adds localized timestamps, a display `content_html`, a plain
text `content_text` and a derived `edited` flag::

    >>> raw = remarks.get_records(sample, field)[0]
    >>> data = remarks.localize_record(raw, sample, request)
    >>> data["edited"]
    False
    >>> "content_html" in data
    True
    >>> "content_text" in data
    True

`get_localized_records` returns the records newest first, with per-record
`can_edit` and `can_delete` flags::

    >>> localized = remarks.get_localized_records(sample, field, request)
    >>> localized[0]["can_edit"]
    True
    >>> localized[0]["can_delete"]
    True

A deleted record exposes the deletion info but keeps its original content::

    >>> raw = remarks.get_records(sample, field)[0]
    >>> remarks.apply_delete(raw, user_id="admin")["deleted"] != ""
    True
    >>> data = remarks.localize_record(raw, sample, request)
    >>> data["is_deleted"]
    True
    >>> data["deleted_by"]
    'admin'
    >>> "First remark" in data["content_html"]
    True


Widget attributes
.................

`get_i18n_labels` returns the translated labels for the React widget::

    >>> labels = remarks.get_i18n_labels()
    >>> sorted(labels.keys())
    ['add_remarks', 'cancel', 'confirm_delete', 'delete', 'deleted_note', 'edit', 'edited', 'hide_history', 'no_remarks', 'original', 'placeholder', 'save', 'show_history', 'show_less', 'show_more', 'sort_newest', 'sort_oldest']

`get_widget_attributes` builds the JSON-encoded `data-*` attributes::

    >>> import json
    >>> attrs = remarks.get_widget_attributes(sample, field, request)
    >>> sorted(attrs.keys())
    ['data-can_add', 'data-can_manage', 'data-current_user_id', 'data-fieldname', 'data-i18n', 'data-id', 'data-portal_url', 'data-remarks', 'data-uid']
    >>> json.loads(attrs["data-fieldname"])
    u'Remarks'
    >>> isinstance(json.loads(attrs["data-remarks"]), list)
    True
