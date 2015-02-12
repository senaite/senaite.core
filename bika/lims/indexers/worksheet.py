from bika.lims.interfaces import IWorksheet, IBatch
from plone.indexer import indexer


@indexer(IWorksheet)
def Priority(instance):
    priority = instance.getPriority()
    if priority:
        return priority.getSortKey()


@indexer(IWorksheet)
def BatchUID(instance):
    if IBatch.providedBy(instance.aq_parent):
        return instance.aq_parent.UID()
