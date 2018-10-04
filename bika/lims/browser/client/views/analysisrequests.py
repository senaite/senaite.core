# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.browser.analysisrequest import AnalysisRequestsView


class ClientAnalysisRequestsView(AnalysisRequestsView):

    def __init__(self, context, request):
        super(ClientAnalysisRequestsView, self).__init__(context, request)
        self.contentFilter['path'] = {
            "query": "/".join(context.getPhysicalPath()),
            "level": 0}
        self.remove_column('Client')
