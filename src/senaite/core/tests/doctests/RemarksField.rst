Remarks field
-------------

The Remarks field stores an append-only history of remark records. Each record
keeps the author, the creation date and the content. Records can be edited in
place, keeping the prior content as a version, and the unified endpoints work
for both the Archetypes and the Dexterity field.

Running this test from the buildout directory::

    bin/test test_textual_doctests -t RemarksField


Test Setup
..........

Needed Imports::

    >>> import json
    >>> from bika.lims import api
    >>> from bika.lims.api.security import get_user_id
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from senaite.core.api import remarks as remarks_api
    >>> from senaite.core.events.remarks import IRemarksChangedEvent
    >>> from senaite.core.z3cform.widgets.remarks.widget import AjaxAddRemark
    >>> from senaite.core.z3cform.widgets.remarks.widget import AjaxEditRemark
    >>> from DateTime import DateTime

Functional Helpers::

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

Variables::

    >>> date_now = timestamp()
    >>> portal = self.portal
    >>> request = self.request
    >>> setup = portal.setup
    >>> bika_setup = portal.bika_setup

Test user::

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])


Create a Sample
...............

    >>> clients = portal.clients
    >>> client = api.create(clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(client, "Contact", Firstname="Rita", Surname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", Prefix="water", MinimumVolume="100 ml")
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Water")
    >>> service = api.create(bika_setup.bika_analysisservices, "AnalysisService", title="pH", Keyword="PH", Category=category)
    >>> values = {
    ...     "Client": client.UID(),
    ...     "Contact": contact.UID(),
    ...     "SamplingDate": date_now,
    ...     "DateSampled": date_now,
    ...     "SampleType": sampletype.UID(),
    ... }
    >>> sample = create_analysisrequest(client, request, values, [service.UID()])
    >>> field = sample.getField("Remarks")

The pure helper functions of the remarks API are covered in `API_remarks`.


Add and edit on the field
.........................

Adding a remark returns the new record::

    >>> first = field.add(sample, "First remark")
    >>> "First remark" in first["content"]
    True
    >>> first["modified"]
    ''
    >>> first["versions"]
    []

Content is sanitized on the way in::

    >>> evil = field.add(sample, "<script>alert(1)</script>safe")
    >>> "<script>" in evil["content"]
    False

Editing keeps the prior content as a version::

    >>> created_before = first["created"]
    >>> edited = field.edit(sample, first["id"], "First remark (edited)")
    >>> "First remark (edited)" in edited["content"]
    True
    >>> edited["modified"] != ""
    True
    >>> len(edited["versions"])
    1
    >>> "First remark" in edited["versions"][0]["content"]
    True
    >>> edited["created"] == created_before
    True


Widget data attributes
......................

The field builds the JSON-encoded `data-*` attributes consumed by the React
widget::

    >>> attrs = field.get_input_widget_attributes(sample, request)
    >>> sorted(attrs.keys())
    ['data-can_add', 'data-can_manage', 'data-current_user_id', 'data-fieldname', 'data-i18n', 'data-id', 'data-portal_url', 'data-remarks', 'data-uid']
    >>> json.loads(attrs["data-fieldname"])
    u'Remarks'
    >>> isinstance(json.loads(attrs["data-remarks"]), list)
    True


Edit permissions
................

A manager may edit any remark, even one authored by somebody else::

    >>> other = {"user_id": "somebody-else"}
    >>> remarks_api.can_manage_remarks(sample)
    True
    >>> remarks_api.can_edit_record(sample, other)
    True

A non-manager who is not the author may not edit the record::

    >>> setRoles(portal, TEST_USER_ID, ['Owner',])
    >>> remarks_api.can_manage_remarks(sample)
    False
    >>> remarks_api.can_edit_record(sample, other)
    False

Restore the manager role::

    >>> setRoles(portal, TEST_USER_ID, ['Manager',])


Endpoints emit the change event
...............................

We capture all fired events to assert the remarks change event::

    >>> from zope.event import subscribers
    >>> captured = []
    >>> subscribers.append(captured.append)

Adding a remark through the endpoint succeeds and returns the localized
record::

    >>> request.form["fieldName"] = "Remarks"
    >>> request.form["uid"] = sample.UID()
    >>> request.form["value"] = "Endpoint remark"
    >>> result = json.loads(AjaxAddRemark(sample, request)())
    >>> result["success"]
    True
    >>> "Endpoint remark" in result["remark"]["content"]
    True

A single change event was fired with the `added` action and the acting user::

    >>> changed = [e for e in captured if IRemarksChangedEvent.providedBy(e)]
    >>> len(changed)
    1
    >>> changed[0].action
    'added'
    >>> changed[0].actor == get_user_id()
    True

Editing the same remark through the endpoint fires an `edited` event::

    >>> request.form["remark_id"] = result["remark"]["id"]
    >>> request.form["value"] = "Endpoint remark (edited)"
    >>> result = json.loads(AjaxEditRemark(sample, request)())
    >>> result["success"]
    True
    >>> changed = [e for e in captured if IRemarksChangedEvent.providedBy(e)]
    >>> changed[-1].action
    'edited'

Cleanup::

    >>> subscribers.remove(captured.append)
