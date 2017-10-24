from bika.lims.interfaces import IAnalysisCategory
from plone.indexer import indexer


@indexer(IAnalysisCategory)
def sortable_title(instance):
    sort_key = instance.getSortKey()
    # noinspection PyBroadException
    try:
        return "{:010.3f}{}".format(sort_key, instance.Title())
    except:
        return instance.Title()
