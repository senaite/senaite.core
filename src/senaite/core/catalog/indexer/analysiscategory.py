# -*- coding: utf-8 -*-

from bika.lims.interfaces import IAnalysisCategory
from plone.indexer import indexer
from Products.CMFPlone.utils import safe_callable
from senaite.core.catalog.utils import sortable_sortkey_title


@indexer(IAnalysisCategory)
def sortable_title(instance):
    title = sortable_sortkey_title(instance)
    if safe_callable(title):
        title = title()
    return title
