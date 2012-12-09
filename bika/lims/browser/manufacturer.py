from bika.lims.controlpanel.bika_instruments import InstrumentsView

class ManufacturerInstrumentsView(InstrumentsView):

    def __init__(self, context, request):
        super(ManufacturerInstrumentsView, self).__init__(context, request)
        self.contentFilter['getManufacturerUID']=self.context.UID()
