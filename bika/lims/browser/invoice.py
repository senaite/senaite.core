# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.browser import BrowserView
from bika.lims.interfaces import IInvoiceView
from zope.interface import implements


class InvoiceView(BrowserView):
    implements(IInvoiceView)

    def __init__(self, context, request):
        super(InvoiceView, self).__init__(context, request)
        self.context = context
        self.request = request
