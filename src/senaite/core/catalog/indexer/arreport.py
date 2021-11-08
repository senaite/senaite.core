# -*- coding: utf-8 -*-

from bika.lims.interfaces import IARReport
from plone.indexer import indexer


@indexer(IARReport)
def sample_uid(instance):
    """Returns a list of UIDs of the contained Samples
    """
    return instance.getRawContainedAnalysisRequests()
