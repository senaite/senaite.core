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
from bika.lims.interfaces import IInvoiceView
from zope.interface import implements


class InvoiceView(BrowserView):
    """Base view for invoices

    This view returns the invoice PDF
    """
    implements(IInvoiceView)

    def __init__(self, context, request):
        super(InvoiceView, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        filename = "invoice.pdf"
        pdf = self.context.getInvoicePDF()
        if pdf:
            data = pdf.data
        else:
            ar = self.context.getAnalysisRequest()
            so = self.context.getSupplyOrder()
            context = ar or so
            view = api.get_view("invoice_create", context=context)
            data = view.create_pdf()
            self.context.setInvoicePDF(data)
        return self.download(data, filename)

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
