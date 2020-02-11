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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

import itertools
import re

from bika.lims import api
from bika.lims.api.snapshot import get_last_snapshot
from bika.lims.api.snapshot import get_snapshot_count
from bika.lims.api.snapshot import get_snapshot_metadata
from bika.lims.api.snapshot import get_snapshots
from bika.lims.api.user import get_user_id
from bika.lims.interfaces import IAuditable, IAuditLogCatalog
from plone.indexer import indexer
from plone.memoize.ram import DontCache
from plone.memoize.ram import cache

UID_RX = re.compile(r"[a-z0-9]{32}$")
DATE_RX = re.compile(r"\d{4}[-/]\d{2}[-/]\d{2}")


def _uid_to_title_cache_key(func, uid):
    brain = api.get_brain_by_uid(uid, default=None)
    if brain is None:
        raise DontCache
    modified = api.get_modification_date(brain).millis()
    return "{}-{}".format(uid, modified)


@cache(_uid_to_title_cache_key)
def get_title_or_id_from_uid(uid):
    """Returns the title or ID from the given UID
    """
    obj = api.get_object_by_uid(uid, default=None)
    if obj is None:
        return ""
    title_or_id = api.get_title(obj) or api.get_id(obj)
    return title_or_id


def get_meta_value_for(snapshot, key, default=None):
    """Returns the metadata value for the given key
    """
    metadata = get_snapshot_metadata(snapshot)
    return metadata.get(key, default)


def get_actor(snapshot):
    """Get the actor of the snapshot
    """
    actor = get_meta_value_for(snapshot, "actor")
    if not actor:
        return get_user_id()
    return actor


def get_fullname(snapshot):
    """Get the actor's fullname of the snapshot
    """
    actor = get_actor(snapshot)
    properties = api.get_user_properties(actor)
    return properties.get("fullname", actor)


def get_action(snapshot):
    """Get the action of the snapshot
    """
    action = get_meta_value_for(snapshot, "action")
    if not action:
        return "Edit"
    return action


def get_created(snapshot):
    """Get the created date of the snapshot
    """
    created = get_meta_value_for(snapshot, "snapshot_created")
    if not created:
        return ""
    return created


@indexer(IAuditable)
def actor(instance):
    """Last modifiying user
    """
    last_snapshot = get_last_snapshot(instance)
    return get_actor(last_snapshot)


@indexer(IAuditable)
def fullname(instance):
    """Last modifiying user
    """
    last_snapshot = get_last_snapshot(instance)
    return get_fullname(last_snapshot)


@indexer(IAuditable)
def modifiers(instance):
    """Returns a list of all users that modified
    """
    snapshots = get_snapshots(instance)
    return map(get_actor, snapshots)


@indexer(IAuditable)
def action(instance):
    """Returns the last performed action
    """
    last_snapshot = get_last_snapshot(instance)
    return get_action(last_snapshot)


@indexer(IAuditable, IAuditLogCatalog)
def listing_searchable_text(instance):
    """Fulltext search for the audit metadata
    """
    # get all snapshots
    snapshots = get_snapshots(instance)
    # extract all snapshot values, because we are not interested in the
    # fieldnames (keys)
    values = map(lambda s: s.values(), snapshots)
    # prepare a set of unified catalog data
    catalog_data = set()
    # values to skip
    skip_values = ["None", "true", "True", "false", "False"]
    # internal uid -> title cache
    uid_title_cache = {}

    # helper function to recursively unpack the snapshot values
    def append(value):
        if isinstance(value, (list, tuple)):
            map(append, value)
        elif isinstance(value, (dict)):
            map(append, value.items())
        elif isinstance(value, basestring):
            # convert unicode to UTF8
            if isinstance(value, unicode):
                value = api.safe_unicode(value).encode("utf8")
            # skip single short values
            if len(value) < 2:
                return
            # flush non meaningful values
            if value in skip_values:
                return
            # flush ISO dates
            if re.match(DATE_RX, value):
                return
            # fetch the title
            if re.match(UID_RX, value):
                if value in uid_title_cache:
                    value = uid_title_cache[value]
                else:
                    title_or_id = get_title_or_id_from_uid(value)
                    uid_title_cache[value] = title_or_id
                    value = title_or_id
            catalog_data.add(value)

    # extract all meaningful values
    for value in itertools.chain(values):
        append(value)

    return " ".join(catalog_data)


@indexer(IAuditable)
def snapshot_created(instance):
    """Snapshot created date
    """
    last_snapshot = get_last_snapshot(instance)
    snapshot_created = get_created(last_snapshot)
    return api.to_date(snapshot_created)


@indexer(IAuditable)
def snapshot_version(instance):
    """Snapshot created date
    """
    return get_snapshot_count(instance)
