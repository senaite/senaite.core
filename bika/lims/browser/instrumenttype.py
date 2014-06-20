from bika.lims.controlpanel.bika_instruments import InstrumentsView
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t

class InstrumentTypeInstrumentsView(InstrumentsView):

    def __init__(self, context, request):
        super(InstrumentTypeInstrumentsView, self).__init__(context, request)
        url = self.portal.absolute_url()
        url += "/bika_setup/bika_instruments/"
        self.context_actions = {_('Add'):
                                {'url': url+'createObject?type_name=Instrument',
                                 'icon': '++resource++bika.lims.images/add.png'}}

    def folderitems(self):
        items = InstrumentsView.folderitems(self)
        filtered_items = []
        for item in items:
            if 'obj' not in item:
                continue
            itype = item['obj'].getInstrumentType()
            if itype and itype.UID() == self.context.UID():
                filtered_items.append(item)
        return filtered_items
