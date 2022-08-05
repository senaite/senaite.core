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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import bikaMessageFactory as _
from bika.lims.browser import BrowserView
from senaite.core.exportimport import instruments


class ExportView(BrowserView):
    """
    """
    def __call__(self):
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
            
        # search instruments classes for 'exim' class or module
        exim = instruments.getExim(exim) if instruments.getExim(exim) else instruments.getExim(exim.lower())
        
        if not exim:
            self.context.plone_utils.addPortalMessage(
                _("Instrument exporter not found"), 'error')
            self.request.RESPONSE.redirect(self.context.absolute_url())
            return

        exporter = exim.Export(self.context, self.request)
        exporter(self.context.getAnalyses())
        pass
