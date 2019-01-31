# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.

from Products.Five.browser import BrowserView


class DownloadView(BrowserView):
    """Download View
    """

    def __init__(self, context, request):
        super(DownloadView, self).__init__(context, request)

    def __call__(self):
        ar = self.context.getAnalysisRequest()
        filename = "{}.pdf".format(ar.getId())
        pdf = self.context.getPdf()
        self.download(pdf.data, filename)

    def download(self, data, filename, content_type="application/pdf"):
        """Download the PDF
        """
        self.request.response.setHeader(
            "Content-Disposition", "inline; filename=%s" % filename)
        self.request.response.setHeader("Content-Type", content_type)
        self.request.response.setHeader("Content-Length", len(data))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.write(data)
