# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.content.abstractanalysis import AbstractAnalysis
from bika.lims.interfaces import IBaseAnalysis
from plone.indexer import indexer
from Products.CMFPlone.utils import safe_callable
from senaite.core.catalog.utils import sortable_sortkey_title


@indexer(IBaseAnalysis)
def sortable_title(instance):
    title = sortable_sortkey_title(instance)
    if safe_callable(title):
        title = title()

    # if analyte, keep them sorted as they were defined in the service by user,
    # but prepend multi-component's sortable title to ensure that multi is
    # always returned first to make things easier
    if isinstance(instance, AbstractAnalysis):
        multi = instance.getMultiComponentAnalysis()
        if multi:
            title = api.get_title(instance)
            service = multi.getAnalysisService()
            analytes = service.getAnalytes()
            titles = filter(None, [an.get("title") for an in analytes])
            index = titles.index(title) if title in titles else len(titles)
            title = "{}-{:04d}".format(sortable_title(multi)(), index)

    return "{}-{}".format(title, api.get_id(instance))
