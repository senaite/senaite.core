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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.interfaces import IListingSearchableTextProvider
from plone.indexer import indexer
from senaite.core import logger
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.interfaces import ISampleCatalog
from zope.component import getAdapters


@indexer(IAnalysisRequest)
def assigned_state(instance):
    """Returns `assigned`, `unassigned` or 'not_applicable' depending on the
    state of the analyses the analysisrequest contains. Return `unassigned` if
    the Analysis Request has at least one 'active' analysis in `unassigned`
    status. Returns 'assigned' if all 'active' analyses of the sample are
    assigned to a Worksheet. Returns 'not_applicable' if no 'active' analyses
    for the given sample exist
    """
    assigned = False
    skip_statuses = ["retracted", "rejected", "cancelled"]

    # Retrieve analyses directly from the instance container instead of relying
    # on ARAnalysesField getter, that performs a catalog query. Reason is, that
    # we never know if the sample is indexed before the analyses or any other
    # dependent catalog
    for analysis in instance.objectValues(spec="Analysis"):
        status = api.get_review_status(analysis)

        if status == "unassigned":
            # One unassigned found, no need to go further
            return "unassigned"

        if status in skip_statuses:
            # Skip "inactive" analyses
            continue

        if analysis.getWorksheetUID():
            # At least one analysis with a worksheet assigned
            assigned = True

    # ARAnalysesField getter returns all the analyses from the sample, those
    # from partitions included. Since we do not rely on the getter, we need to
    # manually extract the analyses from the partitions
    # Pity is, that for the retrieval of partitions we need to rely on a
    # query against uid_catalog (get_backreferences)
    for partition in instance.getDescendants():
        # Note we call this same index, but for the partition
        partition_status = assigned_state(partition)()
        if partition_status == "unassigned":
            # One of the partitions with unassigned, no need to go further
            return "unassigned"

        elif partition_status == "assigned":
            assigned = True

    if assigned:
        # All "active" analyses assigned to a worksheet
        return "assigned"

    # Sample without "active" assigned/unassigned analyses
    return "not_applicable"


@indexer(IAnalysisRequest)
def is_received(instance):
    """Returns whether the Analysis Request has been received
    """
    if instance.getDateReceived():
        return True
    return False


@indexer(IAnalysisRequest, ISampleCatalog)
def listing_searchable_text(instance):
    """Retrieves most commonly searched values for samples

    :returns: string with search terms
    """
    entries = set()

    for obj in [instance] + instance.getDescendants():
        entries.add(obj.getId())
        entries.add(obj.getClientOrderNumber())
        entries.add(obj.getClientReference())
        entries.add(obj.getClientSampleID())

        # we use this approach to bypass the computed fields
        client = obj.getClient()
        entries.add(client.getName())
        entries.add(client.getClientID())

        sampletype = obj.getSampleType()
        entries.add(sampletype.Title() if sampletype else '')

        samplepoint = obj.getSamplePoint()
        entries.add(samplepoint.Title() if samplepoint else '')

        batch = obj.getBatch()
        entries.add(batch.getId() if batch else '')

    catalog = api.get_tool(SAMPLE_CATALOG)
    text_providers = getAdapters((instance, api.get_request(), catalog),
                                 IListingSearchableTextProvider)
    # BBB
    bbb_text_providers = getAdapters((instance, catalog),
                                     IListingSearchableTextProvider)

    # combine the adapters for backwards compatibility
    adapters = list(text_providers) + list(bbb_text_providers)

    # Allow to extend search tokens via adapters
    for name, adapter in adapters:
        try:
            value = adapter()
        except (AttributeError, TypeError, api.APIError) as exc:
            logger.error(exc)
            value = []

        if isinstance(value, (list, tuple)):
            values = map(api.to_searchable_text_metadata, value)
            entries.update(values)
        else:
            value = api.to_searchable_text_metadata(value)
            entries.add(value)

    # Remove empties
    entries = filter(None, entries)

    return u" ".join(map(api.safe_unicode, entries))
