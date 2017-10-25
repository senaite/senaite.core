from bika.lims.interfaces import IAnalysisService
from plone.indexer import indexer
from Products.CMFPlone.CatalogTool import sortable_title as _sortable_title


@indexer(IAnalysisService)
def sortable_title(instance):
    sort_key = instance.getSortKey()
    if sort_key is not None:
        sort_key = 999999
    title = _sortable_title(instance)
    if callable(title):
        title = title()
    return "{:010.3f}{}".format(sort_key, title)
