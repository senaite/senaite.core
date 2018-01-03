# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AnalysisRequestRejectEmailView(BrowserView):
    """
    View that renders the template to be attached in the body of the email
    for the notification of an Analysis Request rejection action.
    """

    template = ViewPageTemplateFile("templates/analysisrequest_retract_mail.pt")

    def __init__(self, context, request):
        super(AnalysisRequestRejectEmailView, self).__init__(context, request)

    def __call__(self):
        return self.template()


class AnalysisRequestRejectPdfView(BrowserView):
    """
    View that renders the template to be used for the generation of a pdf to
    be attached in the email for the notification of an Analysis Request
    rejection action.
    """

    template = ViewPageTemplateFile("templates/analysisrequest_retract_pdf.pt")

    def __init__(self, context, request):
        super(AnalysisRequestRejectPdfView, self).__init__(context, request)

    def __call__(self):
        return self.template()
