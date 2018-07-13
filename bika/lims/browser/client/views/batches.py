# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.browser.batchfolder import BatchFolderContentsView


class ClientBatchesView(BatchFolderContentsView):
    def __init__(self, context, request):
        super(ClientBatchesView, self).__init__(context, request)
        self.view_url = self.context.absolute_url() + "/batches"

    def __call__(self):
        self.contentFilter['getClientUID'] = self.context.UID()
        return BatchFolderContentsView.__call__(self)
