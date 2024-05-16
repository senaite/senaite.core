# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.controlpanel.bika_instruments import InstrumentsView
from senaite.core.permissions import AddInstrumentType


class InstrumentTypeInstrumentsView(InstrumentsView):

    def __init__(self, context, request):
        super(InstrumentTypeInstrumentsView, self).__init__(context, request)
        url = self.portal.absolute_url()
        url += "/bika_setup/bika_instruments/"

        self.context_actions = {
            _(u"listing_instruments_action_add", default=u"Add"): {
                "url": url+"createObject?type_name=Instrument",
                "permission": AddInstrumentType,
                "icon": "senaite_theme/icon/plus",
            }}

    def isItemAllowed(self, obj):
        obj = api.get_object(obj)
        itype = obj.getInstrumentType() if obj else None
        return itype.UID() == self.context.UID() if itype else False
