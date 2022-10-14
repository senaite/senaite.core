# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.interfaces import IAnalysisRequest
from plone.indexer import indexer
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.catalog.utils import get_searchable_text_tokens
from senaite.core.interfaces import ISampleCatalog


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
    """Retrieves all the values of metadata columns in the catalog for
    wildcard searches
    :return: all metadata values joined in a string
    """
    entries = set()
    catalog = SAMPLE_CATALOG

    # add searchable text tokens for the root sample
    tokens = get_searchable_text_tokens(instance, catalog)
    entries.update(tokens)

    # add searchable text tokens for descendant samples
    for descendant in instance.getDescendants():
        tokens = get_searchable_text_tokens(descendant, catalog)
        entries.update(tokens)

    return u" ".join(list(entries))
