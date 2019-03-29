# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims.browser.analysisrequest import AnalysisRequestsView as BaseView


class AnalysisRequestsView(BaseView):

    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'AnalysisRequest',
                              'getBatchUID': api.get_uid(self.context),
                              'sort_on': 'created',
                              'sort_order': 'reverse',
                              'is_active': True}
