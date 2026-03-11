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

import transaction
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Products.Five.browser import BrowserView
from bika.lims import api
from zope.annotation.interfaces import IAnnotations

from senaite.core.queue import JOB_QUEUE_KEY

logger = logging.getLogger("senaite.core.heartbeat")

#: Maximum number of jobs processed in a single heartbeat cycle.
BATCH_SIZE = 50

#: Number of times a job is retried before being discarded.
MAX_RETRIES = 3


class HeartbeatView(BrowserView):
    """Called periodically by the senaite.core background heartbeat thread.

    Drains the heartbeat job queue in batches. Each job runs in its own
    transaction under the security context of the user that enqueued it.

    Add-ons can extend the dispatcher by subclassing and registering this
    view on a more specific layer, or by adding ``handle_<action>`` methods.
    """

    def __call__(self):
        logger.debug("Heartbeat: %s", self.context.getId())
        self.run()
        return "OK"

    def run(self):
        """Process a batch of pending jobs from the queue."""
        jobs = self.get_pending_jobs()
        if not jobs:
            return
        logger.info("Processing %d heartbeat job(s)", len(jobs))
        for job in jobs:
            self.execute_job(job)

    # ------------------------------------------------------------------
    # Queue access
    # ------------------------------------------------------------------

    def get_pending_jobs(self):
        """Return up to BATCH_SIZE jobs from the queue."""
        annotations = IAnnotations(self.context)
        queue = annotations.get(JOB_QUEUE_KEY, [])
        return list(queue[:BATCH_SIZE])

    def discard_job(self, job):
        """Remove a completed or permanently failed job from the queue."""
        annotations = IAnnotations(self.context)
        queue = annotations.get(JOB_QUEUE_KEY)
        if queue is not None and job in queue:
            queue.remove(job)

    # ------------------------------------------------------------------
    # Job execution
    # ------------------------------------------------------------------

    def execute_job(self, job):
        """Run a single job in its own transaction as the job's user."""
        user = self._get_user(job.user_id)
        if user is None:
            logger.error(
                "Cannot execute job %r: user '%s' not found — discarding",
                job, job.user_id)
            self._save_retry(job, discard=True)
            return

        newSecurityManager(None, user)
        try:
            transaction.begin()
            self.dispatch(job)
            self.discard_job(job)
            transaction.commit()
            logger.debug("Job executed: %r", job)
        except Exception:
            transaction.abort()
            logger.exception("Job failed: %r", job)
            self._save_retry(job)
        finally:
            noSecurityManager()

    def _save_retry(self, job, discard=False):
        """Persist an incremented retry count, or discard if limit reached."""
        try:
            transaction.begin()
            job.retries += 1
            if discard or job.retries >= MAX_RETRIES:
                self.discard_job(job)
                logger.error(
                    "Job discarded after %d retries: %r", job.retries, job)
            else:
                logger.warning(
                    "Job will retry (%d/%d): %r",
                    job.retries, MAX_RETRIES, job)
            transaction.commit()
        except Exception:
            transaction.abort()
            logger.exception("Failed to save retry state for job: %r", job)

    def dispatch(self, job):
        """Route a job to its handler method ``handle_<action>``."""
        handler = getattr(self, "handle_" + job.action, None)
        if handler is None:
            raise ValueError(
                "No handler for job action '{}'. "
                "Expected method 'handle_{}'.".format(
                    job.action, job.action))
        handler(job)

    # ------------------------------------------------------------------
    # Built-in handlers
    # ------------------------------------------------------------------

    def handle_reindex(self, job):
        """Reindex an object by UID.

        Expected payload: {"uid": "<object UID>"}
        Optional payload: {"indexes": ["<index1>", ...]}
        """
        uid = job.payload.get("uid")
        if not uid:
            raise ValueError("handle_reindex: missing 'uid' in payload")
        obj = api.get_object_by_uid(uid, default=None)
        if obj is None:
            logger.warning("handle_reindex: object not found for UID %s", uid)
            return
        indexes = job.payload.get("indexes", [])
        obj.reindexObject(idxs=indexes)
        logger.debug("Reindexed %s (indexes=%r)", uid, indexes or "all")

    def handle_transition(self, job):
        """Fire a workflow transition on an object.

        Expected payload: {"uid": "<object UID>", "transition": "<id>"}
        """
        uid = job.payload.get("uid")
        transition = job.payload.get("transition")
        if not uid or not transition:
            raise ValueError(
                "handle_transition: 'uid' and 'transition' required")
        obj = api.get_object_by_uid(uid, default=None)
        if obj is None:
            logger.warning(
                "handle_transition: object not found for UID %s", uid)
            return
        api.do_transition_for(obj, transition)
        logger.debug("Transitioned %s -> %s", uid, transition)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_user(self, user_id):
        """Return the Plone user for user_id, or None if not found."""
        acl_users = getattr(self.context, "acl_users", None)
        if acl_users is None:
            return None
        return acl_users.getUserById(user_id)
