# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.interfaces import IAnalysisRequest
from plone.indexer import indexer
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.catalog.utils import get_searchable_text_tokens
from senaite.core.interfaces import ISampleCatalog


@indexer(IAnalysisRequest)
def assigned_state(instance):
    """Returns `assigned` or `unassigned` depending on the state of the
    analyses the analysisrequest contains. Return `unassigned` if the Analysis
    Request has at least one analysis in `unassigned` state.
    Otherwise, returns `assigned`
    """
    analyses = instance.getAnalyses()
    if not analyses:
        return "unassigned"
    for analysis in analyses:
        analysis_object = api.get_object(analysis)
        if not analysis_object.getWorksheet():
            return "unassigned"
    return "assigned"


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
