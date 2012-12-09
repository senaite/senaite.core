from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.controlpanel.bika_instruments import InstrumentsView
from Products.CMFCore.utils import getToolByName
from zope.interface.declarations import implements
from bika.lims import bikaMessageFactory as _

class ManufacturerInstrumentsView(InstrumentsView):

    def __init__(self, context, request):
        super(ManufacturerInstrumentsView, self).__init__(context, request)
        self.contentFilter['getManufacturerUID']=self.context.UID()
