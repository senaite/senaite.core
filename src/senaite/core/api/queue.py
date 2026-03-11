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

import logging

from persistent.list import PersistentList
from plone import api
from zope.annotation.interfaces import IAnnotations

from senaite.core.queue import HeartbeatJob
from senaite.core.queue import JOB_QUEUE_KEY

logger = logging.getLogger("senaite.core.queue")


def get_queue(portal=None):
    """Return the persistent job queue for the given portal.

    Creates the queue on first access. Uses the current site if no portal
    is given.
    """
    if portal is None:
        portal = api.portal.get()
    annotations = IAnnotations(portal)
    if JOB_QUEUE_KEY not in annotations:
        annotations[JOB_QUEUE_KEY] = PersistentList()
    return annotations[JOB_QUEUE_KEY]


def enqueue(action, payload=None, user_id=None, portal=None):
    """Add a job to the heartbeat queue.

    :param action: String key mapping to ``handle_<action>`` on the view.
    :param payload: Dict with action-specific data (must be ZODB-serialisable).
    :param user_id: Plone user ID to run the job as. Defaults to the current
                    user. Falls back to the site owner if no user is active.
    :param portal: Plone site root. Defaults to the current site.
    """
    if user_id is None:
        try:
            user_id = api.user.get_current().getId()
        except Exception:
            user_id = "admin"

    job = HeartbeatJob(action=action, user_id=user_id, payload=payload)
    queue = get_queue(portal=portal)
    queue.append(job)
    logger.debug("Enqueued job: %r", job)
    return job


def queue_length(portal=None):
    """Return the number of pending jobs in the queue."""
    return len(get_queue(portal=portal))


def clear_queue(portal=None):
    """Remove all pending jobs from the queue."""
    queue = get_queue(portal=portal)
    del queue[:]
    logger.info("Heartbeat queue cleared")
