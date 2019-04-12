# -*- coding: utf-8 -*-

import json

from bika.lims import api
from bika.lims import logger
from bika.lims.api.security import get_roles
from bika.lims.api.security import get_user_id
from bika.lims.interfaces import IAuditable
from DateTime import DateTime
from persistent.list import PersistentList
from senaite.core.supermodel import SuperModel
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAnnotations
from zope.interface import alsoProvides

SNAPSHOT_STORAGE = "senaite.core.snapshots"


def get_storage(obj):
    """Get or create the audit log storage for the given object
    """
    annotation = IAnnotations(obj)
    if annotation.get(SNAPSHOT_STORAGE) is None:
        annotation[SNAPSHOT_STORAGE] = PersistentList()
    return annotation[SNAPSHOT_STORAGE]


def has_snapshots(obj):
    """Checks if the object has snapshots
    """
    storage = get_storage(obj)
    return len(storage) > 0


def get_request_metadata():
    """Get request based metadata
    """
    # get the request
    request = api.get_request()

    # Happens in the test runner
    if not request:
        return {}

    return {
        "comments": request.form.get("comments", ""),
        "remote_address": request.get_header("REMOTE_ADDR"),
        "user_agent": request.get_header("HTTP_USER_AGENT"),
        "referer": request.get_header("HTTP_REFERER"),
    }


def make_metadata_for(obj, **kw):
    """Creates some metadata for the passed in object
    """

    # inject metadata of volatile data
    metadata = {
        "actor": get_user_id(),
        "roles": get_roles(),
        "action": "",
        "review_state": api.get_review_status(obj),
        "active": api.is_active(obj),
        "modified": api.get_modification_date(obj).ISO(),
        "remote_address": "",
        "user_agent": "",
        "referer": "",
        "comments": "",
    }

    # Update request based metadata
    metadata.update(get_request_metadata())

    # allow metadata overrides
    metadata.update(kw)

    return metadata


def take_snapshot(obj, **kw):
    """Takes a snapshot of the passed in object
    """
    logger.debug("📷 Take new snapshot for {}".format(repr(obj)))

    # take a snapshot
    model = SuperModel(obj)
    try:
        snapshot = model.to_dict()
    except Exception as exc:
        # Fails for DuplicateAnalysis `getBulkPrice` with an AttributeError
        logger.error("Failed to create snapshot for {}: {}"
                     .format(repr(obj), str(exc)))
        return

    # generate the metadata
    metadata = make_metadata_for(obj, **kw)

    # store the metadata
    snapshot["metadata"] = metadata

    # get the snapshot storage
    storage = get_storage(obj)

    # save the snapshot as JSON
    storage.append(json.dumps(snapshot))

    # Mark the content as auditable
    alsoProvides(obj, IAuditable)


def is_auditable(obj):
    """Checks if the object is autiable

    Only objects which can hold an annotation storage can be auditable
    """
    return IAnnotatable.providedBy(obj)


def ObjectTransitionedEventHandler(obj, event):
    """Object has been transitioned to an new state
    """

    # only snapshot supported objects
    if not is_auditable(obj):
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
        timestamp = entry.get("time", DateTime())
        entry["time"] = timestamp.ISO()
        entry["modified"] = timestamp.ISO()
        entry["action"] = event.action

    # take a new snapshot
    take_snapshot(obj, **entry)


def ObjectModifiedEventHandler(obj, event):
    """Object has been modified
    """

    # only snapshot supported objects
    if not is_auditable(obj):
        return

    # take a new snapshot
    take_snapshot(obj, action="edit")


def ObjectInitializedEventHandler(obj, event):
    """Object has been created
    """

    # only snapshot supported objects
    if not is_auditable(obj):
        return

    # object has already snapshots
    if has_snapshots(obj):
        return

    # take a new snapshot
    take_snapshot(obj, action="create")
