# -*- coding: utf-8 -*-

from bika.lims.interfaces import IAnalysisRequest
from plone.indexer import indexer
from senaite.core.api.catalog import get_searchable_text_tokens
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.interfaces import ISampleCatalog


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
