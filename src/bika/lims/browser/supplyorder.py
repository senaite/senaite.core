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

from operator import itemgetter
from operator import methodcaller

from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.utils import createPdf
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class View(BrowserView):
    """Supply Order View
    """

    content = ViewPageTemplateFile("templates/supplyorder_content.pt")
    template = ViewPageTemplateFile("templates/supplyorder_view.pt")
    title = _("Supply Order")

    def __init__(self, context, request):
        super(View, self).__init__(context, request)
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/supplyorder_big.png")

    def __call__(self):
        context = self.context
        portal = self.portal
        setup = portal.bika_setup

        # Collect general data
        self.orderDate = self.ulocalized_time(context.getOrderDate())
        self.contact = context.getContact()
        self.contact = self.contact.getFullname() if self.contact else ""
        self.subtotal = "%.2f" % context.getSubtotal()
        self.vat = "%.2f" % context.getVATAmount()
        self.total = "%.2f" % context.getTotal()
        # Set the title
        self.title = context.Title()
        # Collect order item data
        items = context.supplyorder_lineitems

        self.items = []
        for item in items:
            prodid = item["Product"]
            product = setup.bika_labproducts[prodid]
            price = float(item["Price"])
            vat = float(item["VAT"])
            qty = float(item["Quantity"])
            self.items.append({
                "title": product.Title(),
                "description": product.Description(),
                "volume": product.getVolume(),
                "unit": product.getUnit(),
                "price": price,
                "vat": "%s%%" % vat,
                "quantity": qty,
                "totalprice": "%.2f" % (price * qty)
            })
        self.items = sorted(self.items, key=itemgetter("title"))
        # Render the template
        return self.template()

    def getPreferredCurrencyAbreviation(self):
        return self.context.bika_setup.getCurrency()


class EditView(BrowserView):
    """Supply Order Edit View
    """

    template = ViewPageTemplateFile("templates/supplyorder_edit.pt")
    field = ViewPageTemplateFile("templates/row_field.pt")

    def __call__(self):
        portal = self.portal
        request = self.request
        context = self.context
        setup = portal.bika_setup
        # Allow adding items to this context
        context.setConstrainTypesMode(0)
        # Collect the products
        products = setup.bika_labproducts.objectValues("LabProduct")

        # Handle for submission and regular request
        if "submit" in request:
            portal_factory = getToolByName(context, "portal_factory")
            context = portal_factory.doCreate(context, context.id)
            context.processForm()
            # Clear the old line items
            context.supplyorder_lineitems = []
            # Process the order item data
            for prodid, qty in request.form.items():
                if prodid.startswith("product_") and qty and float(qty) > 0:
                    prodid = prodid.replace("product_", "")
                    product = setup.bika_labproducts[prodid]
                    context.supplyorder_lineitems.append(
                            {"Product": prodid,
                             "Quantity": qty,
                             "Price": product.getPrice(),
                             "VAT": product.getVAT()})

            # Redirect to the list of orders
            obj_url = context.absolute_url_path()
            request.response.redirect(obj_url)
            return
        else:
            self.orderDate = context.Schema()["OrderDate"]
            self.contact = context.Schema()["Contact"]
            self.subtotal = "%.2f" % context.getSubtotal()
            self.vat = "%.2f" % context.getVATAmount()
            self.total = "%.2f" % context.getTotal()
            # Prepare the products
            items = context.supplyorder_lineitems
            self.products = []
            products = sorted(products, key=methodcaller("Title"))
            for product in products:
                item = [o for o in items if o["Product"] == product.getId()]
                quantity = item[0]["Quantity"] if len(item) > 0 else 0
                self.products.append({
                    "id": product.getId(),
                    "title": product.Title(),
                    "description": product.Description(),
                    "volume": product.getVolume(),
                    "unit": product.getUnit(),
                    "price": product.getPrice(),
                    "vat": "%s%%" % product.getVAT(),
                    "quantity": quantity,
                    "total": (float(product.getPrice()) * float(quantity)),
                })
            # Render the template
            return self.template()

    def getPreferredCurrencyAbreviation(self):
        return self.context.bika_setup.getCurrency()


class PrintView(View):
    """Supply Order Print View
    """
    template = ViewPageTemplateFile('templates/supplyorder_print.pt')

    def __call__(self):
        html = super(PrintView, self).__call__()
        pdf = createPdf(html)
        filename = "{}.pdf".format(self.context.getId())
        return self.download(pdf, filename)

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
