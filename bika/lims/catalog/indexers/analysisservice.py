from bika.lims.interfaces import IAnalysisService
from plone.indexer import indexer


@indexer(IAnalysisService)
def sortable_title(instance):
    sort_key = instance.getSortKey()
    try:
        return "{:010.3f}{}".format(sort_key, instance.Title())
    except (ValueError, TypeError):
        return instance.Title()
