# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api

from bika.lims.browser.bika_listing import BikaListingView
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import currency_format, get_link, get_email_link
import csv
from cStringIO import StringIO


class InvoiceBatchInvoicesView(BikaListingView):

    def __init__(self, context, request):
        super(InvoiceBatchInvoicesView, self).__init__(context, request)
        self.contentFilter = {
            'portal_type': 'Invoice',
            'path': {
                "query": "/".join(self.context.getPhysicalPath()),
                "level": 0
            },
        }
        self.title = context.Title()
        self.description = ""
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_all_checkbox = False
        self.show_select_column = True
        self.show_all = True
        self.pagesize = 25
        request.set('disable_border', 1)
        self.context_actions = {}
        self.columns = {
            'id': {
                'title': _('Invoice Number'),
                'toggle': True
            },
            'client': {
                'title': _('Client'),
                'toggle': True
            },
            'email': {
                'title': _('Email Address'),
                'toggle': False
            },
            'phone': {
                'title': _('Phone'),
                'toggle': False
            },
            'invoicedate': {
                'title': _('Invoice Date'),
                'toggle': True
            },
            'startdate': {
                'title': _('Start Date'),
                'toggle': False
            },
            'enddate': {
                'title': _('End Date'),
                'toggle': False
            },
            'subtotal': {
                'title': _('Subtotal'),
                'toggle': False
            },
            'vatamount': {
                'title': _('VAT'),
                'toggle': False
            },
            'total': {
                'title': _('Total'),
                'toggle': True
            },
        }
        self.review_states = [
            {
                'id': 'default',
                'contentFilter': self.contentFilter,
                'title': _('Default'),
                'transitions': [],
                'columns': [
                    'id',
                    'client',
                    'email',
                    'phone',
                    'invoicedate',
                    'startdate',
                    'enddate',
                    'subtotal',
                    'vatamount',
                    'total',
                ],
            },
        ]

    def folderitem(self, obj, item, idx):
        """
        Replace or add the required/wanted fields for each invoice
        in the item dictionary

        :param obj: the instance of the class to be foldered. In our case, an
                    Invoice
        :param item: dict containing the properties of the object to be used by
                     the template
        :return: dictionary with the updated fields of the invoice being processed
        """
        currency = currency_format(self.context, 'en')
        item['replace']['id'] = get_link(api.get_url(obj), obj.getId())
        client = obj.getClient()
        if client:
            item['client'] = client.Title()
            item['replace']['client'] = get_link(client.absolute_url(), item['client'])
            item['email'] = client.getEmailAddress()
            item['replace']['email'] = get_email_link(client.getEmailAddress())
            item['phone'] = client.getPhone()
        else:
            item['client'] = ''
            item['email'] = ''
            item['phone'] = ''

        item['invoicedate'] = self.ulocalized_time(obj.getInvoiceDate())
        item['startdate'] = self.ulocalized_time(obj.getBatchStartDate())
        item['enddate'] = self.ulocalized_time(obj.getBatchEndDate())
        item['subtotal'] = currency(obj.getSubtotal())
        item['vatamount'] = currency(obj.getVATAmount())
        item['total'] = currency(obj.getTotal())

        return item


class BatchFolderExportCSV(InvoiceBatchInvoicesView):

    def __call__(self, REQUEST, RESPONSE):
        """
        Export invoice batch into csv format.
        Writes the csv file into the RESPONSE to allow
        the file to be streamed to the user.
        Nothing gets returned.
        """
        delimiter = ','
        filename = 'invoice_batch.txt'
        # Getting the invoice batch
        container = self.context
        assert container
        container.plone_log("Exporting InvoiceBatch to CSV format for PASTEL")
        # Getting the invoice batch's invoices:
        # Since BatchFolderExportCSV does not provide an initializer method
        # (__init__) then the base class initializer is called automatically
        # and we can use the already defined contentFilter to retrieve the
        # invoice batch invoices
        invoices = map(api.get_object, api.search(self.contentFilter, 'portal_catalog'))
        if not len(invoices):
            container.plone_log("InvoiceBatch contains no entries")

        csv_rows = [['Invoice Batch']]
        # Invoice batch header
        csv_rows.append(['ID', container.getId()])
        csv_rows.append(['Invoice Batch Title', container.title])
        csv_rows.append(['Start Date', container.getBatchStartDate().strftime('%Y-%m-%d')])
        csv_rows.append(['End Date', container.getBatchEndDate().strftime('%Y-%m-%d')])
        csv_rows.append([])

        # Building the invoice field header
        csv_rows.append(['Invoices'])
        csv_rows.append(['Invoice ID', 'Client ID', 'Client Name', 'Account Num.', 'Phone', 'Date', 'Total Price'])
        invoices_items_rows = []
        for invoice in invoices:
            # Building the invoice field header
            invoice_info_header = [invoice.getId(),
                                   invoice.getClient().getId(),
                                   invoice.getClient().getName(),
                                   invoice.getClient().getAccountNumber(),
                                   invoice.getClient().getPhone(),
                                   invoice.getInvoiceDate().strftime('%Y-%m-%d'),
                                   ]
            csv_rows.append(invoice_info_header)
            # Obtaining and sorting all analysis items. These analysis are saved inside a list to add later
            items = invoice.invoice_lineitems
            mixed = [(item.get('OrderNumber', ''), item) for item in items]
            mixed.sort()
            # Defining each analysis row
            for line in mixed:
                invoice_analysis = [line[1].get('ItemDate', ''),
                                    line[1].get('ItemDescription', ''),
                                    line[1].get('OrderNumber', ''),
                                    line[1].get('Subtotal', ''),
                                    line[1].get('VATAmount', ''),
                                    line[1].get('Total', ''),
                                    ]
                invoices_items_rows.append(invoice_analysis)

        csv_rows.append([])
        # Creating analysis items header
        csv_rows.append(['Invoices items'])
        csv_rows.append(['Date', 'Description', 'Order', 'Amount', 'VAT', 'Amount incl. VAT'])
        # Adding all invoices items
        for item_row in invoices_items_rows:
            csv_rows.append(item_row)

        # convert lists to csv string
        ramdisk = StringIO()
        writer = csv.writer(ramdisk, delimiter=delimiter)
        assert writer
        writer.writerows(csv_rows)
        result = ramdisk.getvalue()
        ramdisk.close()
        # stream file to browser
        setheader = RESPONSE.setHeader
        setheader(
            'Content-Length',
            len(result)
        )
        setheader(
            'Content-Type',
            'text/x-comma-separated-values'
        )
        setheader(
            'Content-Disposition',
            'inline; filename=%s' % filename)
        RESPONSE.write(result)
