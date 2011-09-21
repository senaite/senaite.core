from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import logger, bikaMessageFactory as _
from openpyxl.reader.excel import load_workbook

class LoadSetupData(BrowserView):
    template = ViewPageTemplateFile("templates/load_setup_data.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.title = _("Load Setup Data")
        self.description = _("Please browse your local machine to select a dataset to load.")

    def __call__(self):
        form = self.request.form
##        fn = join(Globals.INSTANCE_HOME,'var','ar_results.html'),
##                    "w").write(ar_results)
        wb = load_workbook(filename = r'empty_book.xlsx')
        sheet_ranges = wb.get_sheet_by_name(name = 'range names')
        print sheet_ranges.cell('D18').value # D18
        return self.template()

