from bika.lims.controlpanel.bika_instruments import InstrumentsView

class InstrumentTypeInstrumentsView(InstrumentsView):

    def __init__(self, context, request):
        super(InstrumentTypeInstrumentsView, self).__init__(context, request)
        self.contentFilter['getInstrumentTypeUID']=self.context.UID()
