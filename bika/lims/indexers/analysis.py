from bika.lims.interfaces import IAnalysis
from plone.indexer import indexer


@indexer(IAnalysis)
def Priority(instance):
    parent = instance.aq_parent
    if hasattr(parent, 'getPriority'):
        priority = parent.getPriority()
        if priority:
            return priority.getSortKey()
