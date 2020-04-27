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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims.jsonapi import load_field_values
from bika.lims.interfaces import IJSONReadExtender, IAnalysisProfile
from zope.component import adapts
from zope.interface import implements


class JSONReadExtender(object):
    """- Place additional information about profile services
    into the returned records.
    Used in AR Add to prevent extra requests
    """

    implements(IJSONReadExtender)
    adapts(IAnalysisProfile)

    def __init__(self, context):
        self.context = context

    def __call__(self, request, data):
        service_data = []
        for service in self.context.getService():
            this_service = {'UID': service.UID(),
                            'Title': service.Title(),
                            'Keyword': service.getKeyword(),
                            'Price': service.getPrice(),
                            'VAT': service.getVAT(),
                            'PointOfCapture': service.getPointOfCapture(),
                            'CategoryTitle': service.getCategory().Title()}
            service_data.append(this_service)
        data['service_data'] = service_data

