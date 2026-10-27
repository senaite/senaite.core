# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

import json
from collections import Counter

import six
from bika.lims import _
from bika.lims import api
from bika.lims import logger
from bika.lims.api.security import get_roles
from bika.lims.api.security import get_user_id
from bika.lims.interfaces import IAuditable
from bika.lims.interfaces import IDoNotSupportSnapshots
from DateTime import DateTime
from persistent.list import PersistentList
from plone.memoize.ram import cache
from senaite.app.supermodel import SuperModel
from senaite.core.api import dtime
from senaite.core.i18n import translate
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAnnotations
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

SNAPSHOT_STORAGE = "senaite.core.snapshots"


def _objectdata_cache_key(func, obj):
    """Cache Key for object data
    """
    uid = api.get_uid(obj)
    modified = api.get_modification_date(obj).millis()
    review_state = api.get_review_status(obj)
    return "{}-{}-{}".format(uid, review_state, modified)


def supports_snapshots(obj):
    """Checks if the object supports snapshots

    Only objects which can hold an annotation storage can be auditable

    :param obj: Content object
    :returns: True/False
    """
    if IDoNotSupportSnapshots.providedBy(obj):
        return False
    return IAnnotatable.providedBy(obj)


def get_storage(obj):
    """Get or create the audit log storage for the given object

    :param obj: Content object
    :returns: PersistentList
    """
    annotation = IAnnotations(obj)
    if annotation.get(SNAPSHOT_STORAGE) is None:
        annotation[SNAPSHOT_STORAGE] = PersistentList()
    return annotation[SNAPSHOT_STORAGE]


def get_snapshots(obj):
    """Get all snapshots from the storage

    :param obj: Content object
    :returns: List of snapshot dictionaries
    """
    snapshots = get_storage(obj)
    return map(json.loads, snapshots)


def has_snapshots(obj):
    """Checks if the object has snapshots

    :param obj: Content object
    :returns: True/False
    """
    storage = get_storage(obj)
    return len(storage) > 0


def get_snapshot_count(obj):
    """Returns the number of snapsots

    :param obj: Content object
    :returns: Current snapshots in the storage
    """
    try:
        annotation = IAnnotations(obj)
    except TypeError:
        return 0
    storage = annotation.get(SNAPSHOT_STORAGE, [])
    return len(storage)


def get_version(obj):
    """Returns the version of the object

    NOTE: Object versions start with 0!

    :param obj: Content object
    :returns: Current version of the object or -1
    """
    count = get_snapshot_count(obj)
    return count - 1


def get_snapshot_by_version(obj, version=0):
    """Get a snapshot by version

    Snapshot versions begin with `0`, because this is the first index of the
    storage, which is a list.

    :param obj: Content object
    :param version: The index position of the snapshot in the storage
    :returns: Snapshot at the given index position
    """
    if version < 0:
        return None
    snapshots = get_snapshots(obj)
    if version > len(snapshots) - 1:
        return None
    return snapshots[version]


def get_snapshot_version(obj, snapshot):
    """Returns the version of the given snapshot

    :param obj: Content object
    :param snapshot: Snapshot dictionary
    :returns: Index where the object is located
    """
    snapshots = get_snapshots(obj)
    if snapshot not in snapshots:
        return -1
    return snapshots.index(snapshot)


def get_last_snapshot(obj):
    """Get the last snapshot

    :param obj: Content object
    :returns: Last Snapshot or None
    """
    version = get_version(obj)
    return get_snapshot_by_version(obj, version)


def get_snapshot_created(snapshot):
    """Returns the snapshot creation date

    :param snapshot: Snapshot dictionary
    :returns: DateTime object of the snapshot creation date
    """
    metadata = get_snapshot_metadata(snapshot)
    created = metadata.get("snapshot_created")

    # prefer the timestamp if existing
    timestamp = metadata.get("timestamp")
    if timestamp:
        created = dtime.from_timestamp(timestamp)

    return dtime.to_DT(created)


def get_snapshot_metadata(snapshot):
    """Returns the snapshot metadata

    :param snapshot: Snapshot dictionary
    :returns: Metadata dictionary of the snapshot
    """
    return snapshot.get("__metadata__", {})


@cache(_objectdata_cache_key)
def get_object_data(obj):
    """Get object schema data

    NOTE: We RAM cache this data because it should only change when the object
    was modified!

    XXX: We need to set at least the modification date when we set fields in
    Ajax Listing when we take a snapshot there!

    :param obj: Content object
    :returns: Dictionary of extracted schema data
    """

    try:
        model = SuperModel(obj)
        data = model.to_dict()
    except Exception as exc:
        logger.error("Failed to get schema data for {}: {}"
                     .format(repr(obj), str(exc)))
        data = {}

    return data


def get_request_data(request=None):
    """Get request header/form data

    A typical request behind NGINX looks like this:

    {
        'CONNECTION_TYPE': 'close',
        'CONTENT_LENGTH': '52',
        'CONTENT_TYPE': 'application/x-www-form-urlencoded; charset=UTF-8',
        'GATEWAY_INTERFACE': 'CGI/1.1',
        'HTTP_ACCEPT': 'application/json, text/javascript, */*; q=0.01',
        'HTTP_ACCEPT_ENCODING': 'gzip, deflate, br',
        'HTTP_ACCEPT_LANGUAGE': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        'HTTP_COOKIE': '_ga=GA1.2.1058345096.1522506452; ...',
        'HTTP_HOST': 'senaite.ridingbytes.com',
        'HTTP_ORIGIN': 'https://senaite.ridingbytes.com',
        'HTTP_REFERER': 'https://senaite.ridingbytes.com/clients/client-1/H2O-0054',
        'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
        'HTTP_X_FORWARDED_FOR': '93.238.47.95',
        'HTTP_X_REAL_IP': '93.238.47.95',
        'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest',
        'PATH_INFO': '/VirtualHostBase/https/senaite.ridingbytes.com/senaite/VirtualHostRoot//@@API/update',
        'PATH_TRANSLATED': '/VirtualHostBase/https/senaite.ridingbytes.com/senaite/VirtualHostRoot/@@API/update',
        'QUERY_STRING': '',
        'REMOTE_ADDR': '127.0.0.1',
        'REQUEST_METHOD': 'POST',
        'SCRIPT_NAME': '',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '8081',
        'SERVER_PROTOCOL': 'HTTP/1.0',
        'SERVER_SOFTWARE': 'Zope/(2.13.28, python 2.7.12, linux2) ZServer/1.1',
        'channel.creation_time': 1556086048
    }

    :param request: Request object
    :returns: Dictionary of extracted request header/form data
    """

    if request is None:
        # get the request
        request = api.get_request()

    # Happens in the test runner
    if not request:
        return {}

    # Try to obtain the real IP address of the client
    forwarded_for = request.get_header("X_FORWARDED_FOR")
    real_ip = request.get_header("X_REAL_IP")
    remote_address = request.get_header("REMOTE_ADDR")

    return {
        "comments": request.form.get("comments", ""),
        "remote_address": forwarded_for or real_ip or remote_address,
        "user_agent": request.get_header("HTTP_USER_AGENT"),
        "referer": request.get_header("HTTP_REFERER"),
    }


def get_object_metadata(obj, **kw):
    """Get object metadata

    :param obj: Content object
    :returns: Dictionary of extracted object metadata
    """
    created = DateTime()

    # inject metadata of volatile data
    metadata = {
        "actor": get_user_id(),
        "roles": get_roles(),
        "action": "",
        "review_state": api.get_review_status(obj),
        "active": api.is_active(obj),
        "snapshot_created": created.ISO(),
        "timestamp": dtime.to_timestamp(created),
        "modified": api.get_modification_date(obj).ISO(),
        "remote_address": "",
        "user_agent": "",
        "referer": "",
        "comments": "",
    }

    # Update request data
    metadata.update(get_request_data())

    # allow metadata overrides
    metadata.update(kw)

    return metadata


def take_snapshot(obj, store=True, **kw):
    """Takes a snapshot of the passed in object

    :param obj: Content object
    :returns: New snapshot
    """
    logger.debug("📷 Take new snapshot for {}".format(repr(obj)))

    # get the object data
    snapshot = get_object_data(obj)

    # get the metadata
    metadata = get_object_metadata(obj, **kw)

    # store the metadata
    snapshot["__metadata__"] = metadata

    # convert the snapshot to JSON
    data = json.dumps(snapshot)

    # return immediately
    if not store:
        return snapshot

    # get the snapshot storage
    storage = get_storage(obj)

    # store the snapshot data
    storage.append(data)

    # Mark the content as auditable
    alsoProvides(obj, IAuditable)

    return snapshot


def pause_snapshots_for(obj):
    """Pause snapshots for the given object
    """
    alsoProvides(obj, IDoNotSupportSnapshots)


def resume_snapshots_for(obj):
    """Resume snapshots for the given object
    """
    try:
        noLongerProvides(obj, IDoNotSupportSnapshots)
    except ValueError:
        # Handle ValueError: Can only remove directly provided interfaces.
        # when the interface was directly provided on class level
        pass


def compare_snapshots(snapshot_a, snapshot_b, raw=False):
    """Returns a diff of two given snapshots (dictionaries)

    `snapshot_a` holds the values *before* and `snapshot_b` the values *after*
    the change.

    :param snapshot_a: Snapshot with the values before the change
    :param snapshot_b: Snapshot with the values after the change
    :param raw: True to compare the raw values, e.g. UIDs
    :returns: Dictionary of field/value pairs that differ
    """
    if not all(map(lambda x: isinstance(x, dict),
                   [snapshot_a, snapshot_b])):
        return {}

    # shared cache to memoize UID -> title lookups across all fields
    cache = {}
    diffs = {}
    # iterate the union of keys so fields added or removed between the two
    # snapshots are reported as well
    for key in set(snapshot_a) | set(snapshot_b):
        # skip fields starting with _ or __
        if key.startswith("_"):
            continue
        value_a = snapshot_a.get(key)
        value_b = snapshot_b.get(key)
        # get the diff between the two values
        diff = diff_values(value_a, value_b, raw=raw, cache=cache)
        if diff is not None:
            diffs[key] = diff
    return diffs


def compare_last_two_snapshots(obj, raw=False):
    """Helper to compare the last two snapshots directly
    """

    if get_snapshot_count(obj) < 2:
        return {}

    version = get_version(obj)

    snap1 = get_snapshot_by_version(obj, version - 1)
    snap2 = get_snapshot_by_version(obj, version)

    return compare_snapshots(snap1, snap2, raw=raw)


def diff_values(value_a, value_b, raw=False, cache=None):
    """Returns a diff between two values (`value_a` before, `value_b` after)

    With `raw=True` a list with a single `(value_a, value_b)` tuple is returned
    when the values differ (`None` otherwise), keeping the raw values for
    programmatic use.

    With `raw=False` (default) a structured, human readable diff is returned: a
    flat list of "diff line" dicts that describe element-level changes for
    sequences (added/removed), key-level and row-level changes for records and
    DataGrids, and localized before/after values for scalars. UID references
    are resolved to their title/ID. Returns `None` when the values are equal.

    :param value_a: The value before the change
    :param value_b: The value after the change
    :param raw: True to compare the raw values, e.g. UIDs
    :param cache: Optional dict to memoize UID -> title lookups across fields
    :returns: A list of diff lines, a raw tuple list or None
    """
    if raw:
        if value_a == value_b:
            return None
        return [(value_a, value_b)]

    if cache is None:
        cache = {}
    lines = _diff_lines(value_a, value_b, cache)
    return lines or None


def _diff_line(kind, indent, label=None, before=None, after=None, value=None):
    """Build a single diff line dict consumed by the audit log template
    """
    return {
        "kind": kind,
        "indent": indent,
        "label": label,
        "before": before,
        "after": after,
        "value": value,
    }


def _diff_lines(before, after, cache, indent=0):
    """Return a flat list of diff lines describing the change from `before` to
    `after`: records diffed key by key, sequences element by element and
    scalars as localized before/after values.
    """
    # both sides are records (dicts)
    before_rec = _as_record(before)
    after_rec = _as_record(after)
    if before_rec is not None and after_rec is not None:
        return _record_diff_lines(before_rec, after_rec, cache, indent)

    # both sides are sequences (lists/tuples)
    before_seq = _as_sequence(before)
    after_seq = _as_sequence(after)
    if before_seq is not None and after_seq is not None:
        return _sequence_diff_lines(before_seq, after_seq, cache, indent)

    # scalars (or a type change between a container and a scalar)
    before_str = _format_value(before, cache)
    after_str = _format_value(after, cache)
    if before_str == after_str:
        return []
    return [_diff_line("scalar", indent, before=before_str, after=after_str)]


def _as_record(value):
    """Coerce the value to a record (dict) for diffing, or None if it is a
    non-empty, non-dict value (i.e. not comparable as a record).
    """
    if isinstance(value, dict):
        return value
    if value in (None, "", ()):
        return {}
    return None


def _as_sequence(value):
    """Coerce the value to a sequence (list) for diffing, or None if it is a
    non-empty, non-sequence value (i.e. not comparable as a sequence).
    """
    if isinstance(value, (list, tuple)):
        return list(value)
    if value in (None, "", ()):
        return []
    return None


def _record_diff_lines(before, after, cache, indent):
    """Return the diff lines for two records, listing only the keys whose
    value changed. A single scalar change is collapsed into one labeled line.
    """
    lines = []
    for key in sorted(set(before) | set(after)):
        child = _diff_lines(before.get(key), after.get(key), cache, indent + 1)
        if not child:
            continue
        label = _humanize_key(key)
        if len(child) == 1 and child[0]["label"] is None:
            child[0]["label"] = label
            child[0]["indent"] = indent
            lines.extend(child)
        else:
            lines.append(_diff_line("group", indent, label=label))
            lines.extend(child)
    return lines


def _sequence_diff_lines(before, after, cache, indent):
    """Return the diff lines for two sequences. Sequences of records (e.g.
    DataGrid rows) are aligned by position and diffed row by row; plain value
    sequences (e.g. UID references) are diffed element by element.
    """
    has_records = any(isinstance(x, dict) for x in before + after)
    if has_records:
        return _rows_diff_lines(before, after, cache, indent)
    return _values_diff_lines(before, after, cache, indent)


def _values_diff_lines(before, after, cache, indent):
    """Return added/removed lines for two plain value sequences
    """
    before_vals = [_format_value(x, cache) for x in before]
    after_vals = [_format_value(x, cache) for x in after]
    removed = list((Counter(before_vals) - Counter(after_vals)).elements())
    added = list((Counter(after_vals) - Counter(before_vals)).elements())
    lines = []
    for value in sorted(removed):
        lines.append(_diff_line("removed", indent, value=value))
    for value in sorted(added):
        lines.append(_diff_line("added", indent, value=value))
    return lines


def _rows_diff_lines(before, after, cache, indent):
    """Return the diff lines for two sequences of records, aligned by position
    """
    lines = []
    for idx in range(max(len(before), len(after))):
        row_before = before[idx] if idx < len(before) else None
        row_after = after[idx] if idx < len(after) else None
        label = translate(
            _(u"Row ${num}", mapping={"num": idx + 1}), to_utf8=False)
        if row_before is None:
            lines.append(_diff_line(
                "added", indent, label=label,
                value=_summarize_record(row_after, cache)))
        elif row_after is None:
            lines.append(_diff_line(
                "removed", indent, label=label,
                value=_summarize_record(row_before, cache)))
        else:
            child = _diff_lines(row_before, row_after, cache, indent + 1)
            if child:
                lines.append(_diff_line("group", indent, label=label))
                lines.extend(child)
    return lines


def _summarize_record(record, cache):
    """Return a compact `key=value; ...` summary of a record's non-empty
    values, used when a whole row was added or removed.
    """
    if not isinstance(record, dict):
        return _format_value(record, cache)
    parts = []
    for key in sorted(record):
        value = record.get(key)
        if not value:
            continue
        parts.append(u"{}={}".format(
            _humanize_key(key), _format_value(value, cache)))
    return u"; ".join(parts) or translate(_("Empty"), to_utf8=False)


def _humanize_key(key):
    """Return a human readable label for a record key
    """
    if not isinstance(key, six.string_types):
        return key
    return api.safe_unicode(key)


def _format_value(value, cache):
    """Convert a single value into a human readable, localized string.

    Resolves UID references to their title/ID (memoized in `cache`), formats
    booleans as Yes/No and strips the portal path from physical paths.
    """
    if isinstance(value, bool):
        if value:
            return translate(_("Yes"), to_utf8=False)
        return translate(_("No"), to_utf8=False)
    if isinstance(value, dict):
        return _summarize_record(value, cache)
    if isinstance(value, (list, tuple)):
        return u"; ".join(_format_value(v, cache) for v in value)
    if value in (None, "", ()):
        return translate(_("Not set"), to_utf8=False)
    if isinstance(value, six.string_types):
        # XXX: bad data, e.g. in AS Method field
        if value == "None":
            return translate(_("Not set"), to_utf8=False)
        # 0 is detected as the portal UID
        if value == "0":
            return u"0"
        # remove the portal path to reduce noise in virtual hostings
        if value.startswith("/"):
            portal_path = api.get_path(api.get_portal())
            return api.safe_unicode(value.replace(portal_path, "", 1))
        if api.is_uid(value):
            return _resolve_uid(value, cache)
        return api.safe_unicode(value)
    return api.safe_unicode(str(value))


def _resolve_uid(uid, cache):
    """Resolve a UID to a title/ID, memoized via the given cache dict
    """
    if uid not in cache:
        cache[uid] = _get_title_or_id_from_uid(uid)
    return cache[uid]


def _get_title_or_id_from_uid(uid):
    """Returns the title or ID from the given UID
    """
    try:
        obj = api.get_object_by_uid(uid)
    except api.APIError:
        obj = None
    if not obj:
        return u"<Deleted {}>".format(uid)
    title_or_id = api.get_title(obj) or api.get_id(obj)
    return api.safe_unicode(title_or_id)


def disable_snapshots(obj):
    """Disable and removes all snapshots from the given object
    """
    # do not take more snapshots
    alsoProvides(obj, IDoNotSupportSnapshots)

    # do not display audit log
    noLongerProvides(obj, IAuditable)

    # remove all snapshots
    annotation = IAnnotations(obj)
    storage = annotation.get(SNAPSHOT_STORAGE)
    if storage:
        del(annotation[SNAPSHOT_STORAGE])
