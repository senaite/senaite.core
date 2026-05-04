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

from bika.lims import api
from senaite.core import logger
from senaite.core.catalog import SAMPLE_CATALOG

HAZARD_FIELDS = ("hazardous", "hazard_categories")

# Sample workflow states that are still subject to change. Closed
# states (published, invalid, cancelled, rejected) are skipped on
# reindex because the data is frozen anyway and reindexing them on
# every SampleType edit becomes prohibitive on large databases.
ACTIVE_SAMPLE_STATES = (
    "sample_registered",
    "sample_due",
    "sample_received",
    "to_be_verified",
    "verified",
)


def _hazard_fields_changed(event):
    """True if any hazard-relevant field is in the event description.

    Modification descriptions are emitted by Plone's lifecycleevent
    machinery on edit. When the event carries no descriptions (e.g.
    a programmatic save without a schema diff), assume a change so
    catalog data does not silently drift.
    """
    descriptions = list(getattr(event, "descriptions", None) or [])
    if not descriptions:
        return True
    for description in descriptions:
        attributes = getattr(description, "attributes", ()) or ()
        if any(attr in HAZARD_FIELDS for attr in attributes):
            return True
    return False


def on_sampletype_modified(sample_type, event):
    """Reindex hazard metadata on samples of this type.

    The ``getHazardous`` and ``getHazardCategories`` columns on the
    sample catalog are computed at index time. When the SampleType
    flips one of those flags, the brain copies on the existing
    samples become stale until they are reindexed individually. We
    walk the affected brains here once instead of waking up every
    sample on each listing render.
    """
    if not _hazard_fields_changed(event):
        return
    uid = api.get_uid(sample_type)
    catalog = api.get_tool(SAMPLE_CATALOG)
    brains = catalog({
        "getSampleTypeUID": uid,
        "review_state": list(ACTIVE_SAMPLE_STATES),
    })
    if not brains:
        return
    logger.info(
        "Reindexing hazard metadata on %d active sample(s) of type '%s'",
        len(brains), api.get_id(sample_type))
    for brain in brains:
        sample = api.get_object(brain)
        sample.reindexObject(idxs=["getHazardous", "getHazardCategories"])
