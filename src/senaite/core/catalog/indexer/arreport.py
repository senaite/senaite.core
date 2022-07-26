# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.interfaces import IARReport
from plone.indexer import indexer


@indexer(IARReport)
def sample_uid(instance):
    """Returns a list of UIDs of the contained Samples
    """
    return instance.getRawContainedAnalysisRequests()


@indexer(IARReport)
def arreport_searchable_text(instance):
    sample = instance.getAnalysisRequest()
    metadata = instance.getMetadata() or {}
    tokens = [
        sample.getId(),
        sample.getBatchID(),
        metadata.get("paperformat", ""),
        metadata.get("orientation", ""),
        metadata.get("template", ""),
    ]
    # Extend IDs of contained Samples
    contained_samples = instance.getContainedAnalysisRequests()
    tokens.extend(map(api.get_id, contained_samples))
    return u" ".join(list(set(tokens)))
