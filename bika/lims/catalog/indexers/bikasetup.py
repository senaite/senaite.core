from Products.Archetypes.interfaces import IBaseObject
from plone.indexer import indexer

from bika.lims.interfaces import IBikaSetupCatalog
from bika.lims.interfaces import ISampleTypeAwareMixin


@indexer(ISampleTypeAwareMixin, IBikaSetupCatalog)
def sampletype_uids(instance):
    """Returns the list of SampleType UIDs the instance is assigned to

    This is a KeywordIndex, so it will be indexed as a list, even if only one
    SampleType can be assigned to the instance. Moreover, if the instance has no
    SampleType assigned, it returns a tuple with a None value. This allows
    searches for `MissingValue` entries too.
    """
    return instance.getSampleTypeUID() or (None, )
