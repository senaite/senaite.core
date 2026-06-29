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

"""Shared helpers for the Remarks field, used by both the Archetypes and the
Dexterity field implementations as well as the widget endpoints.

A remark record is a plain dict with the following keys:

    id           Stable identity, used to target edits
    user_id      Original author
    user_name    Original author full name
    created      ISO timestamp of the original content (never changes)
    content      Current (latest) content, sanitized HTML
    modified     ISO timestamp of the last edit ("" => never edited)
    modified_by  User id of the last editor (may differ from the author)
    versions     List of prior versions, newest first, each a dict with
                 {content, created, user_id}

The new keys (modified, modified_by, versions) are optional. Records created
before this feature simply lack them and are read with safe defaults, so no
data migration is required. They are filled lazily on the first edit.
"""

import json
import re

from Products.CMFCore import permissions
from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.api.security import check_permission
from bika.lims.api.security import get_user_id
from bika.lims.interfaces import IRemarksField as IATRemarksField
from bika.lims.utils import tmpID
from senaite.core.api.dtime import now
from senaite.core.api.dtime import to_localized_time
from senaite.core.i18n import translate
from senaite.core.permissions import DeleteRemarks
from senaite.core.permissions import FieldEditRemarks
from senaite.core.permissions import ManageSenaite
from senaite.core.schema.interfaces import IRemarksField as IDXRemarksField

try:
    from html import unescape as html_unescape
except ImportError:  # Python 2
    from HTMLParser import HTMLParser
    html_unescape = HTMLParser().unescape


def to_safe_html(content):
    """Sanitize the given content through the `text/x-html-safe` transform

    :param content: the (plain or HTML) text to sanitize
    :type content: str
    :returns: sanitized, safe HTML
    :rtype: str
    """
    if not content:
        return content
    pt = api.get_tool("portal_transforms")
    stream = pt.convertTo("text/x-html-safe", content)
    return stream.getData()


def to_plain_text(content):
    """Convert (safe) HTML content back to plain text for editing

    Block tags and line breaks become newlines, remaining tags are stripped
    and HTML entities are unescaped. Note: the `portal_transforms`
    `text/plain` transform is not used here because it collapses paragraph and
    line breaks into spaces, which would lose the line structure of remarks.

    :param content: the (safe) HTML content to convert
    :type content: str
    :returns: the plain text representation
    :rtype: unicode
    """
    if not content:
        return ""
    text = api.safe_unicode(content)
    text = re.sub(r"(?i)<\s*br\s*/?\s*>", "\n", text)
    text = re.sub(r"(?i)</\s*(p|div|li)\s*>", "\n", text)
    text = re.sub(r"(?i)<[^>]+>", "", text)
    text = html_unescape(text)
    # collapse runs of blank lines and trim
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def make_record(content, user_id=None, user_name=None):
    """Create a new remark record for the given content

    :param content: the content of the new remark
    :type content: str
    :param user_id: id of the author (defaults to the current user)
    :type user_id: str
    :param user_name: full name of the author (resolved from `user_id` when
                      not provided)
    :type user_name: str
    :returns: a new remark record with sanitized content and empty edit
              metadata
    :rtype: dict
    """
    if user_id is None:
        user_id = get_user_id()
    if user_name is None:
        user_name = api.get_user_fullname(user_id) or user_id
    return {
        "id": tmpID(),
        "user_id": user_id,
        "user_name": user_name,
        "created": now(),
        "content": to_safe_html((content or "").strip()),
        "modified": "",
        "modified_by": "",
        "deleted": "",
        "deleted_by": "",
        "versions": [],
    }


def apply_edit(record, content, editor_id=None):
    """Update the record in place with the new content, keeping the prior
    content as a version

    The current content is pushed onto the front of the `versions` list and
    the `modified` / `modified_by` metadata is stamped. The original `created`
    date and author are preserved.

    :param record: the remark record to edit
    :type record: dict
    :param content: the new content of the remark
    :type content: str
    :param editor_id: id of the editing user (defaults to the current user)
    :type editor_id: str
    :returns: the same record, updated
    :rtype: dict
    """
    if editor_id is None:
        editor_id = get_user_id()

    # the version being replaced: when the current content was authored
    prior = {
        "content": record.get("content", ""),
        "created": record.get("modified") or record.get("created", ""),
        "user_id": record.get("modified_by") or record.get("user_id", ""),
    }
    versions = list(record.get("versions") or [])
    versions.insert(0, prior)

    record["versions"] = versions
    record["content"] = to_safe_html((content or "").strip())
    record["modified"] = now()
    record["modified_by"] = editor_id
    return record


def apply_delete(record, user_id=None):
    """Soft-delete the record in place, stamping who deleted it and when

    The content is kept in storage for audit purposes but is no longer
    exposed for display (see `localize_record`).

    :param record: the remark record to delete
    :type record: dict
    :param user_id: id of the deleting user (defaults to the current user)
    :type user_id: str
    :returns: the same record, marked as deleted
    :rtype: dict
    """
    if user_id is None:
        user_id = get_user_id()
    record["deleted"] = now()
    record["deleted_by"] = user_id
    return record


def apply_restore(record):
    """Restore a soft-deleted record in place by clearing the deletion stamp

    :param record: the remark record to restore
    :type record: dict
    :returns: the same record, no longer marked as deleted
    :rtype: dict
    """
    record["deleted"] = ""
    record["deleted_by"] = ""
    return record


def find_record(records, remark_id):
    """Find a remark record by its id

    :param records: the list of remark records to search
    :type records: list
    :param remark_id: the id of the remark to find
    :type remark_id: str
    :returns: the (index, record) tuple, or (None, None) if not found
    :rtype: tuple
    """
    for index, record in enumerate(records):
        if record.get("id") == remark_id:
            return index, record
    return None, None


def get_remarks_field(obj, field_name):
    """Resolve a remarks field by name, accepting both the AT and DX field
    interfaces

    :param obj: the object holding the field
    :param field_name: the name of the remarks field
    :type field_name: str
    :returns: the remarks field, or None if not found or not a remarks field
    """
    fields = api.get_fields(obj)
    if field_name not in fields:
        return None
    field = fields.get(field_name)
    if IDXRemarksField.providedBy(field) or IATRemarksField.providedBy(field):
        return field
    return None


def get_field_name(field):
    """Return the name of an AT or DX field

    :param field: an Archetypes or Dexterity field
    :returns: the field name
    :rtype: str
    """
    if hasattr(field, "getName"):
        return field.getName()
    return getattr(field, "__name__", "")


def get_records(obj, field):
    """Return the remark records of the field as a list of plain dicts

    :param obj: the object holding the field
    :param field: the remarks field
    :returns: the remark records as plain dicts
    :rtype: list
    """
    records = field.get(obj) or []
    return [dict(record) for record in records]


def can_view_remarks(context):
    """Check if the current user can view the remarks of the context

    :param context: the object to check the permission against
    :returns: True if the current user can view the object
    :rtype: bool
    """
    return check_permission(permissions.View, context)


def can_add_remark(context):
    """Check if the current user can add remarks on the context

    :param context: the object to check the permission against
    :returns: True if the current user can add remarks
    :rtype: bool
    """
    return check_permission(FieldEditRemarks, context)


def can_manage_remarks(context):
    """Check if the current user can manage (administer) remarks on the context

    :param context: the object to check the permission against
    :returns: True if the current user can manage remarks
    :rtype: bool
    """
    return check_permission(ManageSenaite, context)


def can_delete_remarks(context):
    """Check if the current user may delete/restore remarks on the context

    This is the manager override, granted to LabManager / Manager but not to
    LabClerk (see the `senaite.core: Delete Remarks` permission).

    :param context: the object to check the permission against
    :returns: True if the current user may delete/restore remarks
    :rtype: bool
    """
    return check_permission(DeleteRemarks, context)


def can_edit_record(context, record, user_id=None):
    """Check if the current user can edit the given remark record

    Users may only edit their own (not deleted) remarks. Managers do not get
    an edit override; they may delete instead (see `can_delete_record`).

    :param context: the object holding the remark
    :param record: the remark record to check
    :type record: dict
    :param user_id: the acting user id (defaults to the current user)
    :type user_id: str
    :returns: True if the user can edit the record
    :rtype: bool
    """
    if record.get("deleted"):
        return False
    if user_id is None:
        user_id = get_user_id()
    is_owner = user_id == record.get("user_id")
    return bool(is_owner and can_add_remark(context))


def can_delete_record(context, record=None):
    """Check if the current user can delete the given remark record

    Deletion is the manager override: managers may delete any remark that is
    not already deleted. Deletion is a soft-delete (see `apply_delete`).

    :param context: the object holding the remark
    :param record: the remark record to check (optional)
    :type record: dict
    :returns: True if the user can delete the record
    :rtype: bool
    """
    if record is not None and record.get("deleted"):
        return False
    return can_delete_remarks(context)


def can_restore_record(context, record):
    """Check if the current user can restore the given (deleted) remark record

    Restoring is part of the manager override: managers may bring back a
    soft-deleted remark.

    :param context: the object holding the remark
    :param record: the remark record to check
    :type record: dict
    :returns: True if the user can restore the record
    :rtype: bool
    """
    if not (record and record.get("deleted")):
        return False
    return can_delete_remarks(context)


def annotate_permissions(data, context, record, user_id=None):
    """Annotate a localized record with the acting user's action flags

    :param data: the localized record to annotate (mutated in place)
    :type data: dict
    :param context: the object holding the remark
    :param record: the raw remark record the flags are computed from
    :type record: dict
    :param user_id: the acting user id (defaults to the current user)
    :type user_id: str
    :returns: the same `data`, with `can_edit` / `can_delete` / `can_restore`
    :rtype: dict
    """
    if user_id is None:
        user_id = get_user_id()
    data["can_edit"] = can_edit_record(context, record, user_id)
    data["can_delete"] = can_delete_record(context, record)
    data["can_restore"] = can_restore_record(context, record)
    return data


def localize_time(value, context, request):
    """Return the localized representation of an ISO timestamp

    :param value: the ISO timestamp to localize
    :type value: str
    :param context: the context for the localization
    :param request: the current request
    :returns: the localized time, or "" if no value was given
    :rtype: str
    """
    if not value:
        return ""
    return to_localized_time(value, long_format=True,
                             context=context, request=request)


def localize_record(record, context, request):
    """Return a display copy of the record with localized timestamps

    Adds a rendered `content_html` for display, a plain text `content_text`
    for the editor and a derived `edited` flag. Does not mutate the input.

    :param record: the remark record to localize
    :type record: dict
    :param context: the context for the localization
    :param request: the current request
    :returns: a localized copy of the record
    :rtype: dict
    """
    data = dict(record)
    data["created"] = localize_time(record.get("created"), context, request)
    data["modified"] = localize_time(record.get("modified"), context, request)
    data["edited"] = bool(record.get("modified"))
    deleted = record.get("deleted")
    data["deleted"] = localize_time(deleted, context, request)
    data["deleted_by"] = record.get("deleted_by", "")
    data["is_deleted"] = bool(deleted)

    if deleted:
        # the original content is kept in storage for audit but hidden from
        # display; the widget renders a placeholder instead
        data["content_html"] = ""
        data["content_text"] = ""
        data["versions"] = []
        return data

    # content is stored as sanitized HTML; render it as-is and provide a plain
    # text variant for the editor textarea
    content = record.get("content") or ""
    data["content_html"] = content
    data["content_text"] = to_plain_text(content)
    versions = []
    for version in record.get("versions") or []:
        item = dict(version)
        item["created"] = localize_time(
            version.get("created"), context, request)
        item["content_html"] = version.get("content") or ""
        versions.append(item)
    data["versions"] = versions
    return data


def get_localized_records(obj, field, request):
    """Return the field records, newest first, localized and annotated with
    per-record `can_edit` and `can_delete` flags for the current user

    :param obj: the object holding the field
    :param field: the remarks field
    :param request: the current request
    :returns: the localized remark records, newest first
    :rtype: list
    """
    records = get_records(obj, field)
    # raw `created` is ISO, so a reverse string sort yields newest first
    records.sort(key=lambda r: r.get("created") or "", reverse=True)

    user_id = get_user_id()
    out = []
    for record in records:
        data = localize_record(record, obj, request)
        annotate_permissions(data, obj, record, user_id)
        out.append(data)
    return out


def get_i18n_labels():
    """Return the translated labels passed to the React widget

    :returns: a mapping of label key to translated text
    :rtype: dict
    """
    return {
        "add_remarks": translate(_("Add remarks")),
        "save": translate(_("Save")),
        "cancel": translate(_("Cancel")),
        "edit": translate(_("Edit")),
        "edited": translate(_("edited")),
        "delete": translate(_("Delete")),
        "restore": translate(_("Restore")),
        "confirm_delete": translate(_("Delete this remark?")),
        "deleted_note": translate(_("deleted by {user} at {time}")),
        "show_history": translate(_("Show history")),
        "hide_history": translate(_("Hide history")),
        "show_more": translate(_("Show more")),
        "show_less": translate(_("Show less")),
        "sort_newest": translate(_("Newest first")),
        "sort_oldest": translate(_("Oldest first")),
        "placeholder": translate(_("Add a remark...")),
        "no_remarks": translate(_("No remarks yet")),
        "original": translate(_("original")),
    }


def get_widget_attributes(context, field, request):
    """Build the JSON-encoded `data-*` attributes for the React mount element

    Both the AT skins widget and the DX z3cform widget call this so the same
    component is mounted with identical data in every context.

    :param context: the object holding the field
    :param field: the remarks field
    :param request: the current request
    :returns: a mapping of `data-*` attribute name to JSON-encoded value
    :rtype: dict
    """
    field_name = get_field_name(field)
    uid = api.get_uid(context)
    attributes = {
        "data-id": "remarks-{}-{}".format(uid, field_name),
        "data-uid": uid,
        "data-fieldname": field_name,
        "data-portal_url": api.get_url(api.get_portal()),
        "data-remarks": get_localized_records(context, field, request),
        "data-can_add": can_add_remark(context),
        "data-can_manage": can_manage_remarks(context),
        "data-current_user_id": get_user_id(),
        "data-i18n": get_i18n_labels(),
    }
    return {key: json.dumps(value) for key, value in attributes.items()}
