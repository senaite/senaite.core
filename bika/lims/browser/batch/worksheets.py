from bika.lims.browser.worksheetfolder import WorksheetFolderListingView as _WV


class WorksheetFolderListingView(_WV):
    def __init__(self, context, request):
        super(WorksheetFolderListingView, self).__init__(context, request)
        self.view_url = self.context.absolute_url() + "/worksheets"
        if 'path' in self.contentFilter:
            del (self.contentFilter['path'])
        self.contentFilter['BatchUID'] = self.context.UID()
