# coding=utf-8
from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from bika.lims.exportimport import instruments


class ExportView(BrowserView):
    """
    """
    def __call__(self):

        translate = self.context.translate

        instrument = self.context.getInstrument()
        if not instrument:
            self.context.plone_utils.addPortalMessage(
                _("You must select an instrument"), 'info')
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        exim = instrument.getDataInterface()
        if not exim:
            self.context.plone_utils.addPortalMessage(
                _("Instrument has no data interface selected"), 'info')
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        # exim refers to filename in instruments/
        if type(exim) == list:
            exim = exim[0]
        exim = exim.lower()

        # search instruments module for 'exim' module
        if not instruments.getExim(exim):
            self.context.plone_utils.addPortalMessage(
                _("Instrument exporter not found"), 'error')
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        exim = instruments.getExim(exim)
        exporter = exim.Export(self.context, self.request)
        data = exporter(self.context.getAnalyses())
        pass
