from plone.indexer import indexer

from bika.lims import api
from bika.lims.catalog.bika_catalog import BIKA_CATALOG
from bika.lims.interfaces import IBatch, IBikaCatalog


@indexer(IBatch, IBikaCatalog)
def listing_searchable_text(instance):
    entries = set()
    catalog = api.get_tool(BIKA_CATALOG)
    columns = catalog.schema()
    brains = catalog({"UID": api.get_uid(instance)})
    brain = brains[0] if brains else None
    for column in columns:
        brain_value = api.safe_getattr(brain, column, None)
        instance_value = api.safe_getattr(instance, column, None)
        parsed = api.to_searchable_text_metadata(brain_value or instance_value)
        entries.add(parsed)

    # Remove empties
    entries = filter(None, entries)

    # Concatenate all strings to one text blob
    return " ".join(entries)
