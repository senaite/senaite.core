# -*- coding: utf-8 -*-

from bika.lims.catalog.indexers import sortable_sortkey_title
from bika.lims.interfaces import IAnalysisCategory
from plone.indexer import indexer
from Products.CMFPlone.utils import safe_callable


@indexer(IAnalysisCategory)
def sortable_title(instance):
    title = sortable_sortkey_title(instance)
    if safe_callable(title):
        title = title()
    return title
