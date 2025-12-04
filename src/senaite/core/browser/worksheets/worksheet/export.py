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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.Five.browser import BrowserView

from bika.lims import bikaMessageFactory as _
from senaite.core.exportimport import instruments


class ExportView(BrowserView):
    """
    """

    def __init__(self, context, request):
        super(ExportView, self).__init__(context, request)

    def __call__(self):
        instrument = self.context.getInstrument()
        if not instrument:
            msg = _(
                u"select_instrument_message",
                default=u"You must select an instrument",
            )
            self.add_status_message(msg)
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        exim = instrument.getDataInterface()
        if not exim:
            msg = _(
                u"no_data_instrument_message",
                default=u"Instrument has no data interface selected",
            )
            self.add_status_message(msg)
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        # exim refers to filename in instruments/
        if isinstance(exim, list):
            exim = exim[0]
            
        # search instruments classes for 'exim' class or module
        if instruments.getExim(exim):
            exim = instruments.getExim(exim)
        else:
            exim = instruments.getExim(exim.lower())
        
        if not exim:
            msg = _(
                u"instrument_exporter_not_found_message",
                default=u"Instrument exporter not found",
            )
            self.add_status_message(msg, "error")
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        exporter = exim.Export(self.context, self.request)
        exporter(self.context.getAnalyses())
        pass

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)
