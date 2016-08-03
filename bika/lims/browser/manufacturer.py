from bika.lims.controlpanel.bika_instruments import InstrumentsView

class ManufacturerInstrumentsView(InstrumentsView):

    def __init__(self, context, request):
        super(ManufacturerInstrumentsView, self).__init__(context, request)

    def isItemAllowed(self, obj):
        manuf = obj.getManufacturer() if obj else None
        return manuf.UID() == self.context.UID() if manuf else False
