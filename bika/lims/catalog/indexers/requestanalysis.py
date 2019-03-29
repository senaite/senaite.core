# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
