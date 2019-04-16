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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

import json

from bika.lims.api import to_date
from bika.lims.api.user import get_user_id
from bika.lims.interfaces import IAuditable
from bika.lims.subscribers.auditlog import get_storage
from plone.indexer import indexer


def get_snapshots(instance):
    """Get all snapshots from the storage
    """
    snapshots = get_storage(instance)
    return map(json.loads, snapshots)


def get_last_snapshot(instance):
    """Get the last snapshot
    """
    snapshots = get_snapshots(instance)
    if not snapshots:
        return {}
    return snapshots[-1]


def get_meta_value_for(snapshot, key, default=None):
    """Returns the metadata value for the given key
    """
    metadata = snapshot.get("metadata", {})
    return metadata.get(key, default)


def get_actor(snapshot):
    """Get the actor of the snapshot
    """
    actor = get_meta_value_for(snapshot, "actor")
    if not actor:
        return get_user_id()
    return actor


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


@indexer(IAuditable)
def listing_searchable_text(instance):
    """Fulltext search for the audit metadata
    """
    snapshots = get_storage(instance)
    return " ".join(snapshots)


@indexer(IAuditable)
def snapshot_created(instance):
    """Snapshot created date
    """
    last_snapshot = get_last_snapshot(instance)
    snapshot_created = get_created(last_snapshot)
    return to_date(snapshot_created)


@indexer(IAuditable)
def snapshot_version(instance):
    """Snapshot created date
    """
    snapshots = get_storage(instance)
    return len(snapshots)
