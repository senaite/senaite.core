# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import api
from bika.lims.browser.analysisrequest import AnalysisRequestsView as BaseView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


class AnalysisRequestsView(BaseView):
    template = ViewPageTemplateFile(
        "../analysisrequest/templates/analysisrequests.pt")
    implements(IViewView)

    def __init__(self, context, request):
        super(AnalysisRequestsView, self).__init__(context, request)
        self.contentFilter = {'portal_type': 'AnalysisRequest',
                              'getBatchUID': api.get_uid(self.context),
                              'sort_on': 'created',
                              'sort_order': 'reverse',
                              'cancellation_state':'active'}

    def getMemberDiscountApplies(self):
        client = self.context.getClient()
        return client and client.getMemberDiscountApplies() or False

    def getRestrictedCategories(self):
        client = self.context.getClient()
        return client and client.getRestrictedCategories() or []

    def getDefaultCategories(self):
        client = self.context.getClient()
        return client and client.getDefaultCategories() or []
