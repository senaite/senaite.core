# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.interfaces.analysis import IRequestAnalysis
from plone.indexer import indexer


@indexer(IRequestAnalysis)
def getAncestorsUIDs(instance):
    """Returns the UIDs of all the ancestors (Analysis Requests) this analysis
    comes from
    """
    request = instance.getRequest()
    parents = map(lambda ar: api.get_uid(ar), request.getAncestors())
    return [api.get_uid(request)] + parents
