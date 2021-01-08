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

from bika.lims import _
from bika.lims import api
from bika.lims.browser import BrowserView
from bika.lims.interfaces import IAnalysis
from bika.lims.interfaces import IAnalysisProfile
from bika.lims.interfaces import IInvoiceView
from bika.lims.utils import createPdf
from plone.memoize import view
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.app.supermodel.model import SuperModel
from zope.i18n.locales import locales
from zope.interface import alsoProvides
from zope.interface import implements


class InvoiceView(BrowserView):
    """Analyses Invoice View
    """
    implements(IInvoiceView)

    template = ViewPageTemplateFile("templates/invoice.pt")
    print_template = ViewPageTemplateFile("templates/invoice_print.pt")
    content = ViewPageTemplateFile("templates/invoice_content.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        # TODO: Refactor to permission
        # Control the visibility of the invoice create/print document actions
        if api.get_review_status(self.context) in ["verified", "published"]:
            self.request["verified"] = 1
        return self.template()

    @property
    def sample(self):
        """Returns a supermodel of the sample
        """
        return SuperModel(self.context)

    def to_localized_time(self, date, **kw):
        """Converts the given date to a localized time string
        """
        if date is None:
            return ""
        # default options
        options = {
            "long_format": True,
            "time_only": False,
            "context": api.get_portal(),
            "request": api.get_request(),
            "domain": "senaite.core",
        }
        options.update(kw)
        return ulocalized_time(date, **options)

    @view.memoize
    def get_currency_symbol(self):
        """Get the currency Symbol
        """
        locale = locales.getLocale("en")
        setup = api.get_setup()
        currency = setup.getCurrency()
        return locale.numbers.currencies[currency].symbol

    @view.memoize
    def get_decimal_mark(self):
        """Returns the decimal mark
        """
        setup = api.get_setup()
        return setup.getDecimalMark()

    def format_price(self, price):
        """Formats the price with the set decimal mark and currency
        """
        # ensure we have a float
        price = api.to_float(price, default=0.0)
        dm = self.get_decimal_mark()
        cur = self.get_currency_symbol()
        price = "%s %.2f" % (cur, price)
        return price.replace(".", dm)

    def get_billable_items(self):
        """Return a list of billable items
        """
        items = []
        for obj in self.context.getBillableItems():
            if self.is_profile(obj):
                items.append({
                    "obj": obj,
                    "title": obj.Title(),
                    "vat": obj.getAnalysisProfileVAT(),
                    "price": self.format_price(obj.getAnalysisProfilePrice()),
                })
            if self.is_analysis(obj):
                items.append({
                    "obj": obj,
                    "title": obj.Title(),
                    "vat": obj.getVAT(),
                    "price": self.format_price(obj.getPrice()),
                })
        return items

    def is_profile(self, obj):
        """Checks if the object is a profile
        """
        return IAnalysisProfile.providedBy(obj)

    def is_analysis(self, obj):
        """Checks if the object is an analysis
        """
        return IAnalysis.providedBy(obj)

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)


class InvoicePrintView(InvoiceView):
    """Print view w/o outer contents
    """
    template = ViewPageTemplateFile("templates/invoice_print.pt")

    def __call__(self):
        pdf = self.create_pdf()
        filename = "{}.pdf".format(self.context.getId())
        return self.download(pdf, filename)

    def create_pdf(self):
        """Create the invoice PDF
        """
        invoice = self.template()
        return createPdf(invoice)

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


class InvoiceCreate(InvoicePrintView):
    """Create the invoice
    """

    def __call__(self):
        # disable CSRF protection to allow write on read
        alsoProvides(self.request, IDisableCSRFProtection)
        # Create the invoice object and link it to the current AR.
        sample = self.context
        # create first the invoice so that we have a unique invoice ID
        invoice = sample.createInvoice(None)
        # create then the PDF with the invoice ID
        pdf = self.create_pdf()
        # set it to the invoice object
        invoice.setInvoicePDF(pdf)
        # set message and redirect back
        self.add_status_message(_("Invoice {} created").format(
            api.get_id(invoice)))
        self.request.response.redirect(
            "%s/invoice" % sample.absolute_url())
