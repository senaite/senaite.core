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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.browser import BrowserView
from bika.lims.browser.header_table import HeaderTableView
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
        # render header table
        self.header_table = HeaderTableView(self.context, self.request)()

        # Create the ResultsInterpretation by department view
        self.riview = ARResultsInterpretationView(self.context, self.request)

        return self.template()

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
        return self.context.getInvoiceExclude()

    def show_categories(self):
        """Check the setup if analysis services should be categorized
        """
        setup = api.get_setup()
        return setup.getCategoriseAnalysisServices()
