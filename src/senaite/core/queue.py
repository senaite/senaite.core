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

from DateTime import DateTime
from persistent import Persistent

#: Annotation key used to store the job queue on the portal.
JOB_QUEUE_KEY = "senaite.core.heartbeat.queue"


class HeartbeatJob(Persistent):
    """A single unit of deferred work stored in the heartbeat job queue.

    Jobs are created via ``senaite.core.api.queue.enqueue`` and executed
    by ``senaite.core.browser.heartbeat.HeartbeatView``.

    ``action`` maps to a ``handle_<action>`` method on the heartbeat view,
    allowing add-ons to extend the dispatcher without modifying this package.

    ``payload`` is an action-specific plain dict (must be ZODB-serialisable).

    ``user_id`` is the Plone user that will be set as the security manager
    principal when the job runs, ensuring correct permission checks and a
    meaningful audit trail.
    """

    def __init__(self, action, user_id, payload=None):
        self.action = action
        self.user_id = user_id
        self.payload = payload or {}
        self.retries = 0
        self.created = DateTime()

    def __repr__(self):
        return "<HeartbeatJob action={} user={} retries={} created={}>".format(
            self.action, self.user_id, self.retries, self.created)
