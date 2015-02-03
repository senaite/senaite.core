from bika.lims.interfaces import IAnalysisRequest
from plone.indexer import indexer


@indexer(IAnalysisRequest)
def BatchUID(instance):
    batch = instance.getBatch()
    if batch:
        return batch.UID()

@indexer(IAnalysisRequest)
def Priority(instance):
    priority = instance.getPriority()
    if priority:
        return priority.getSortKey()
