# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AnalysisRequestRejectBase(object):
    """
    Provides helper methods that ease the work with rejection reasons
    """

    def get_rejection_reasons(self, keyword=None):
        """
        Returns a list with the rejection reasons as strings

        :param keyword: set of rejection reasons to be retrieved.
        Possible values are:
            - 'selected': Get, amongst the set of predefined reasons, the ones selected
            - 'other': Get the user free-typed reason for rejection
            - None: Get all rejection reasons
        :return: list of rejection reasons as strings or an empty list
        """
        keys = ['selected', 'other']
        if keyword is None:
            return sum(map(self.get_rejection_reasons, keys), [])
        if keyword not in keys:
            return []
        rejection_reasons = self.context.getRejectionReasons()
        rejection_reasons = rejection_reasons and rejection_reasons[0] or {}
        if keyword == 'other':
            return rejection_reasons.get(keyword, '') and [rejection_reasons.get(keyword, '')] or []
        return rejection_reasons.get(keyword, [])


class AnalysisRequestRejectEmailView(BrowserView, AnalysisRequestRejectBase):
    """
    View that renders the template to be attached in the body of the email
    for the notification of an Analysis Request rejection action.
    """

    template = ViewPageTemplateFile("templates/analysisrequest_retract_mail.pt")

    def __init__(self, context, request):
        super(AnalysisRequestRejectEmailView, self).__init__(context, request)

    def __call__(self):
        return self.template()


class AnalysisRequestRejectPdfView(BrowserView, AnalysisRequestRejectBase):
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
