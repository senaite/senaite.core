# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IBikaSetup
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.interfaces import ISetup


class SetupLegacyLinkViewlet(ViewletBase):
    """Viewlet that displays a link between DX and AT setup forms
    """
    index = ViewPageTemplateFile("templates/setup_legacy_link.pt")

    def available(self):
        """Returns True if the viewlet should be displayed
        """
        return True

    def get_target_url(self):
        """Returns the URL to the other setup form
        """
        # Check if we're on the DX SENAITE Setup
        if ISetup.providedBy(self.context):
            # Link to the old Bika Setup (AT)
            bika_setup = api.get_bika_setup()
            if bika_setup:
                return "{}/edit".format(api.get_url(bika_setup))

        # Check if we're on the AT Bika Setup
        elif IBikaSetup.providedBy(self.context):
            # Link to the new SENAITE Setup (DX)
            senaite_setup = api.get_senaite_setup()
            if senaite_setup:
                return "{}/edit".format(api.get_url(senaite_setup))

        return None

    def get_link_text(self):
        """Returns the appropriate link text
        """
        # Check if we're on the DX SENAITE Setup
        if ISetup.providedBy(self.context):
            return _("Legacy LIMS Setup")

        # Check if we're on the AT Bika Setup
        elif IBikaSetup.providedBy(self.context):
            return _("New LIMS Setup")

        return ""
