# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018-2019 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims.browser.analysisrequest import AnalysisRequestsView


class ClientAnalysisRequestsView(AnalysisRequestsView):

    def __init__(self, context, request):
        super(ClientAnalysisRequestsView, self).__init__(context, request)

        self.contentFilter["path"] = {
            "query": api.get_path(context),
            "level": 0}

        self.remove_column("Client")

    def update(self):
        super(ClientAnalysisRequestsView, self).update()

        # always redirect to the /analysisrequets view
        request_path = self.request.PATH_TRANSLATED
        if (request_path.endswith(self.context.getId())):
            object_url = api.get_url(self.context)
            redirect_url = "{}/{}".format(object_url, "analysisrequests")
            self.request.response.redirect(redirect_url)
