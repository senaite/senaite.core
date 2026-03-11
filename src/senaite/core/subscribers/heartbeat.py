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
import os
import threading

import transaction
from Products.CMFPlone.interfaces import IPloneSiteRoot

logger = logging.getLogger("senaite.core.heartbeat")

#: Set to "0", "false", "no" or "off" to disable the heartbeat thread.
ENV_ENABLED = "SENAITE_HEARTBEAT"

#: Seconds between heartbeat cycles. Default: 60.
ENV_INTERVAL = "SENAITE_HEARTBEAT_INTERVAL"

#: Seconds to wait after startup before the first run. Default: 30.
ENV_STARTUP_DELAY = "SENAITE_HEARTBEAT_STARTUP_DELAY"

#: Signals the heartbeat thread to stop cleanly on process shutdown.
_stop_event = threading.Event()


def _is_enabled():
    val = os.environ.get(ENV_ENABLED, "1").strip().lower()
    return val not in ("0", "false", "no", "off")


def _get_interval():
    try:
        return int(os.environ.get(ENV_INTERVAL, "60"))
    except ValueError:
        logger.warning(
            "Invalid value for %s, using default 60s", ENV_INTERVAL)
        return 60


def _get_startup_delay():
    try:
        return int(os.environ.get(ENV_STARTUP_DELAY, "30"))
    except ValueError:
        logger.warning(
            "Invalid value for %s, using default 30s", ENV_STARTUP_DELAY)
        return 30


def iter_plone_sites(app):
    """Yield all PloneSite objects found directly under the Zope app root."""
    for obj in app.objectValues():
        if IPloneSiteRoot.providedBy(obj):
            yield obj


def call_site_heartbeat(site):
    """Call @@heartbeat on a single site via unrestrictedTraverse.

    Transaction management and security context are handled by the view
    on a per-job basis.
    """
    view = site.unrestrictedTraverse("@@heartbeat", None)
    if view is None:
        logger.warning(
            "@@heartbeat view not found for site: %s", site.getId())
        return
    view()


def run_heartbeat_cycle():
    """Open a fresh Zope connection and call @@heartbeat on every PloneSite.

    The view owns transaction management and security per job.
    The ``finally`` block aborts any uncommitted state left over as a
    safety net (e.g. if the view raised before its own commit/abort).
    """
    import Zope2
    from Testing.makerequest import makerequest

    app = None
    try:
        app = makerequest(Zope2.app())
        for site in iter_plone_sites(app):
            try:
                call_site_heartbeat(site)
            except Exception:
                logger.exception(
                    "Heartbeat failed for site: %s", site.getId())
    finally:
        transaction.abort()
        if app is not None:
            app._p_jar.close()


def heartbeat_loop(interval, startup_delay):
    """Background daemon thread: wait for startup, then loop until stopped."""
    logger.info(
        "Heartbeat thread waiting %ds before first run", startup_delay)
    if _stop_event.wait(startup_delay):
        logger.info("Heartbeat thread stopped before first run")
        return
    while not _stop_event.is_set():
        logger.debug("Running heartbeat cycle")
        run_heartbeat_cycle()
        _stop_event.wait(interval)
    logger.info("Heartbeat thread stopped")


def on_process_starting(event):
    """Start the heartbeat background thread when the Zope process starts."""
    if not _is_enabled():
        logger.info("Heartbeat disabled via %s", ENV_ENABLED)
        return
    interval = _get_interval()
    startup_delay = _get_startup_delay()
    _stop_event.clear()
    t = threading.Thread(
        target=heartbeat_loop,
        name="senaite.heartbeat",
        kwargs={"interval": interval, "startup_delay": startup_delay},
    )
    t.daemon = True
    t.start()
    logger.info(
        "Heartbeat thread started (interval: %ds, startup delay: %ds)",
        interval, startup_delay)


def on_process_stopping(event):
    """Signal the heartbeat thread to stop when the Zope process shuts down."""
    logger.info("Signalling heartbeat thread to stop")
    _stop_event.set()
