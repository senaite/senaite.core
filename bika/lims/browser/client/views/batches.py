from bika.lims.browser.batchfolder import BatchFolderContentsView
from Products.CMFCore.utils import getToolByName


class ClientBatchesView(BatchFolderContentsView):
    def __init__(self, context, request):
        super(ClientBatchesView, self).__init__(context, request)
        self.view_url = self.context.absolute_url() + "/batches"

    def __call__(self):
        return BatchFolderContentsView.__call__(self)

    def contentsMethod(self, contentFilter):
        bc = getToolByName(self.context, "bika_catalog")
        batches = {}
        for ar in bc(portal_type='AnalysisRequest',
                     getClientUID=self.context.UID()):
            ar = ar.getObject()
            batch = ar.getBatch()
            if batch is not None:
                batches[batch.UID()] = batch
        return batches.values()
