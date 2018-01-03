# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.CMFPlone.CatalogTool import sortable_title as _sortable_title
from bika.lims.interfaces import IBaseAnalysis
from plone.indexer import indexer


@indexer(IBaseAnalysis)
def sortable_title(instance):
    sort_key = instance.getSortKey()
    if sort_key is None:
        sort_key = 999999
    title = _sortable_title(instance)
    if callable(title):
        title = title()
    return "{:010.3f}{}".format(sort_key, title)
