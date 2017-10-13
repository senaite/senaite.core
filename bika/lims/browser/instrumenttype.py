# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from bika.lims.controlpanel.bika_instruments import InstrumentsView
from bika.lims import bikaMessageFactory as _

class InstrumentTypeInstrumentsView(InstrumentsView):

    def __init__(self, context, request):
        super(InstrumentTypeInstrumentsView, self).__init__(context, request)
        url = self.portal.absolute_url()
        url += "/bika_setup/bika_instruments/"
        self.context_actions = {_('Add'):
                                {'url': url+'createObject?type_name=Instrument',
                                 'icon': '++resource++bika.lims.images/add.png'}}

    def isItemAllowed(self, obj):
        itype = obj.getInstrumentType() if obj else None
        return itype.UID() == self.context.UID() if itype else False
