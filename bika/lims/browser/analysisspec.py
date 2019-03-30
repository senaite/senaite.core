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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims.config import POINTS_OF_CAPTURE
from bika.lims.interfaces import IAnalysisSpec
from bika.lims.interfaces import IJSONReadExtender
from zope.component import adapts
from zope.interface import implements

class JSONReadExtender(object):
    """Adds the UID to the ResultsRange dict.  This will go away
    when we stop using keywords for this stuff.
    """

    implements(IJSONReadExtender)
    adapts(IAnalysisSpec)

    def __init__(self, context):
        self.context = context

    def __call__(self, request, data):
        bsc = self.context.bika_setup_catalog
        rr = []
        for i, x in enumerate(data.get("ResultsRange", [])):
            keyword = x.get("keyword")
            proxies = bsc(portal_type="AnalysisService", getKeyword=keyword)
            if proxies:
                data['ResultsRange'][i]['uid'] = proxies[0].UID
