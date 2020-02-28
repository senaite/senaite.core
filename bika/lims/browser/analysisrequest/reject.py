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

from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AnalysisRequestRejectPdfView(BrowserView):
    """
    View that renders the template to be used for the generation of a pdf to
    be attached in the email for the notification of an Analysis Request
    rejection action.
    """
    template = ViewPageTemplateFile("templates/analysisrequest_retract_pdf.pt")

    def __call__(self):
        return self.template()

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

