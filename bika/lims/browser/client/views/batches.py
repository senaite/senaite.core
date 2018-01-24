# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims.browser.batchfolder import BatchFolderContentsView
from Products.CMFCore.utils import getToolByName
from bika.lims.catalog.analysisrequest_catalog import \
    CATALOG_ANALYSIS_REQUEST_LISTING


class ClientBatchesView(BatchFolderContentsView):
    def __init__(self, context, request):
        super(ClientBatchesView, self).__init__(context, request)
        self.view_url = self.context.absolute_url() + "/batches"

    def __call__(self):
        return BatchFolderContentsView.__call__(self)

    def contentsMethod(self, contentFilter):
        bc = getToolByName(self.context, CATALOG_ANALYSIS_REQUEST_LISTING)
        batches = {}
        for ar in bc(portal_type='AnalysisRequest',
                     getClientUID=self.context.UID()):
            ar = ar.getObject()
            batch = ar.getBatch()
            if batch is not None:
                batches[batch.UID()] = batch
        return batches.values()
