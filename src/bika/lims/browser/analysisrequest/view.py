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

from bika.lims import api
from bika.lims.browser import BrowserView
from bika.lims.browser.header_table import HeaderTableView
from bika.lims.interfaces import IReceived
from bika.lims.interfaces import IVerified
from bika.lims.permissions import EditFieldResults
from bika.lims.permissions import EditResults
from bika.lims.utils import check_permission
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from resultsinterpretation import ARResultsInterpretationView


class AnalysisRequestViewView(BrowserView):
    """Main AR View
    """
    template = ViewPageTemplateFile("templates/analysisrequest_view.pt")

    def __init__(self, context, request):
        self.init__ = super(
            AnalysisRequestViewView, self).__init__(context, request)
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/sample_big.png",
        )

    def __call__(self):
        # If the analysis request has been received and hasn't been yet
        # verified yet, redirect the user to manage_results view, but only if
        # the user has privileges to Edit(Field)Results, cause otherwise she/he
        # will receive an InsufficientPrivileges error!
        if (self.request.PATH_TRANSLATED.endswith(self.context.id) and
            self.can_edit_results() and self.can_edit_field_results() and
           self.is_received() and not self.is_verified()):

            # Redirect to manage results view if not cancelled
            if not self.is_cancelled():
                manage_results_url = "{}/{}".format(
                    self.context.absolute_url(), "manage_results")
                return self.request.response.redirect(manage_results_url)

        # render header table
        self.header_table = HeaderTableView(self.context, self.request)()

        # Create the ResultsInterpretation by department view
        self.riview = ARResultsInterpretationView(self.context, self.request)

        return self.template()

    def render_analyses_table(self, table="lab"):
        """Render Analyses Table
        """
        if table not in ["lab", "field", "qc"]:
            raise KeyError("Table '{}' does not exist".format(table))
        view_name = "table_{}_analyses".format(table)
        view = api.get_view(
            view_name, context=self.context, request=self.request)
        # Call listing hooks
        view.update()
        view.before_render()
        return view.ajax_contents_table()

    def has_lab_analyses(self):
        """Check if the AR contains lab analyses
        """
        # Negative performance impact - add a Metadata column
        analyses = self.context.getAnalyses(getPointOfCapture="lab")
        return len(analyses) > 0

    def has_field_analyses(self):
        """Check if the AR contains field analyses
        """
        # Negative performance impact - add a Metadata column
        analyses = self.context.getAnalyses(getPointOfCapture="field")
        return len(analyses) > 0

    def has_qc_analyses(self):
        """Check if the AR contains field analyses
        """
        # Negative performance impact - add a Metadata column
        analyses = self.context.getQCAnalyses()
        return len(analyses) > 0

    def can_edit_results(self):
        """Checks if the current user has the permission "EditResults"
        """
        return check_permission(EditResults, self.context)

    def can_edit_field_results(self):
        """Checks if the current user has the permission "EditFieldResults"
        """
        return check_permission(EditFieldResults, self.context)

    def is_received(self):
        """Checks if the AR is received
        """
        return IReceived.providedBy(self.context)

    def is_verified(self):
        """Checks if the AR is verified
        """
        return IVerified.providedBy(self.context)

    def is_cancelled(self):
        """Checks if the AR is cancelled
        """
        return api.get_review_status(self.context) == "cancelled"

    def is_hazardous(self):
        """Checks if the AR is hazardous
        """
        return self.context.getHazardous()

    def is_retest(self):
        """Checks if the AR is a retest
        """
        return self.context.getRetest()

    def exclude_invoice(self):
        """True if the invoice should be excluded
        """

    def show_categories(self):
        """Check the setup if analysis services should be categorized
        """
        setup = api.get_setup()
        return setup.getCategoriseAnalysisServices()
