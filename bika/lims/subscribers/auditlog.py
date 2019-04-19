# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.api.snapshot import has_snapshots
from bika.lims.api.snapshot import supports_snapshots
from bika.lims.api.snapshot import take_snapshot
from DateTime import DateTime


def reindex_object(obj):
    """Reindex the object in the `auditlog_catalog` catalog

    This is needed *after* the event handlers fired, because the indexing takes
    place before the snapshot was created.

    Also see here for more details:
    https://docs.plone.org/develop/addons/components/events.html#modified-events

    TL;DR: `Products.Archetypes.interfaces.IObjectEditedEvent` is fired after
    `reindexObject()` is called. If you manipulate your content object in a
    handler for this event, you need to manually reindex new values.
    """
    auditlog_catalog = api.get_tool("auditlog_catalog")
    auditlog_catalog.reindexObject(obj)


def ObjectTransitionedEventHandler(obj, event):
    """Object has been transitioned to an new state
    """

    # only snapshot supported objects
    if not supports_snapshots(obj):
        return

    # default transition entry
    entry = {
        "modified": DateTime().ISO(),
        "action": event.action,
    }

    # get the last history item
    history = api.get_review_history(obj, rev=True)
    if history:
        entry = history[0]
        # make transitions also a modification entry
        timestamp = entry.pop("time", DateTime())
        entry["modified"] = timestamp.ISO()
        entry["action"] = event.action

    # take a new snapshot
    take_snapshot(obj, **entry)

    # reindex the object in the auditlog catalog
    reindex_object(obj)


def ObjectModifiedEventHandler(obj, event):
    """Object has been modified
    """

    # only snapshot supported objects
    if not supports_snapshots(obj):
        return

    # take a new snapshot
    take_snapshot(obj, action="edit")

    # reindex the object in the auditlog catalog
    reindex_object(obj)


def ObjectInitializedEventHandler(obj, event):
    """Object has been created
    """

    # only snapshot supported objects
    if not supports_snapshots(obj):
        return

    # object has already snapshots
    if has_snapshots(obj):
        return

    # take a new snapshot
    take_snapshot(obj, action="create")

    # reindex the object in the auditlog catalog
    reindex_object(obj)
