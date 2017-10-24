from bika.lims.interfaces import IAnalysisCategory
from plone.indexer import indexer


@indexer(IAnalysisCategory)
def sortable_title(instance):
    sort_key = instance.getSortKey()
    try:
        return "{:010.3f}{}".format(sort_key, instance.Title())
    except (ValueError, TypeError):
        return instance.Title()
