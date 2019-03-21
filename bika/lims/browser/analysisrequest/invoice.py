# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims.browser import BrowserView
from bika.lims.interfaces import IAnalysis
from bika.lims.interfaces import IAnalysisProfile
from bika.lims.interfaces import IInvoiceView
from plone.memoize import view
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.supermodel.model import SuperModel
from zope.i18n.locales import locales
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


class InvoicePrintView(InvoiceView):
    """Print view w/o outer contents
    """
    template = ViewPageTemplateFile("templates/invoice_print.pt")


class InvoiceCreate(InvoiceView):
    """Create the invoice
    """

    def __call__(self):
        # Create the invoice object and link it to the current AR.
        self.context.createInvoice()

        # Reload the page to see the the new fields
        self.request.response.redirect(
            "%s/invoice" % self.aq_parent.absolute_url())
