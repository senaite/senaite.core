# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2023 by it's authors.
# Some rights reserved, see README and LICENSE.

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
