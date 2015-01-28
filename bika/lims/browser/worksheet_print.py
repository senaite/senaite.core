# coding=utf-8
from bika.lims import logger
from bika.lims.browser import BrowserView
from bika.lims.utils import to_utf8, createPdf
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class WorksheetPrintView(BrowserView):
    """ Print view for a worksheet. This view acts as a placeholder, so
        the user can select the preferred options (AR by columns, AR by
        rows, etc.) for printing. Both a print button and pdf button
        are shown.
    """

    template = ViewPageTemplateFile("templates/worksheet_print.pt")
    _layout = 'worksheet_print_ar_by_row.pt'
    _current_ws_index = 0
    _worksheets = []

    def __init__(self, context, request):
        super(WorksheetPrintView, self).__init__(context, request)
        self._worksheets = [self.context]


    def __call__(self):
        """ Entry point of WorksheetPrintView.
            If context.portal_type is a Worksheet, then the PrintView
            is initialized to manage only that worksheet. If the
            context.portal_type is a WorksheetFolder and there are
            items selected in the request (items param), the PrintView
            will show the preview for all the selected Worksheets.
            By default, returns a HTML-encoded template, but if the
            request contains a param 'pdf' with value 1, will flush a
            pdf for the worksheet.
        """

        if self.context.portal_type == 'Worksheet':
            self._worksheets = [self.context]

        elif self.context.portal_type == 'WorksheetFolder' \
            and self.request.get('items', ''):
            uids = self.request.get('items').split(',')
            uc = getToolByName(self.context, 'uid_catalog')
            self._worksheets = [obj.getObject() for obj in uc(UID=uids)]

        else:
            # Warn and redirect to referer
            logger.warning('WorksheetPrintView: type not allowed: %s' %
                            self.context.portal_type)
            self.destination_url = self.request.get_header("referer",
                                   self.context.absolute_url())

        # Generate PDF?
        if self.request.form.get('pdf', '0') == '1':
            return self._flush_pdf()
        else:
            return self.template()


    def getWorksheets(self):
        """ Returns the list of worksheets to be printed
        """
        return self._worksheets;


    def nextWorksheet(self):
        """ Returns the next worksheet from the list. Returns None when
            the iterator reaches the end of the array. Use the call
            beginWorksheetsIterator() to start again.
        """
        ws = None
        if self.current_ws_index < len(self._worksheets):
            ws = self._worksheets[self._current_ws_index]
            self._current_ws_index += 1
        return ws


    def beginWorksheetsIterator(self):
        """ Resets the ws iterator
        """
        self._current_ws_index = 0

    def _flush_pdf():
        """ Generates a PDF using the current layout as the template and
            returns the chunk of bytes.
        """
        return ""