from bika.lims.interfaces import IWorksheet
from plone.indexer import indexer


@indexer(IWorksheet)
def Priority(instance):
    priority = instance.getPriority()
    if priority:
        return priority.getSortKey()
