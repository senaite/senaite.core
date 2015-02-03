from bika.lims.interfaces import IBatch
from plone.indexer import indexer


@indexer(IBatch)
def BatchDate(instance):
    return instance.Schema().getField('BatchDate').get(instance)
