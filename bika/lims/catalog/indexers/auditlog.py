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


def get_actor(snapshot):
    """Get the actor of the snapshot
    """
    metadata = snapshot.get("metadata", {})
    actor = metadata.get("actor")
    if not actor:
        return get_user_id()
    return actor


@indexer(IAuditable)
def actor(instance):
    """Last modifiying user
    """
    snapshots = get_snapshots(instance)
    last_snapshot = snapshots[-1]
    return get_actor(last_snapshot)


@indexer(IAuditable)
def modifiers(instance):
    """Returns a list of all users that modified
    """
    snapshots = get_snapshots(instance)
    return map(get_actor, snapshots)


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
    metadata = last_snapshot.get("metadata", {})
    snapshot_created = metadata.get("snapshot_created")
    return to_date(snapshot_created)


@indexer(IAuditable)
def snapshot_version(instance):
    """Snapshot created date
    """
    snapshots = get_storage(instance)
    return len(snapshots)
