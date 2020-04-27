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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SenaiteSetupButtonViewlet(ViewletBase):
    """Renders a Button to navigate to the Setup View
    """
    index = ViewPageTemplateFile("templates/setupbutton.pt")

    def update(self):
        super(SenaiteSetupButtonViewlet, self).update()
        self.portal = api.get_portal()
        portal_url = self.portal.absolute_url()
        self.setup_url = "/".join([portal_url, "@@lims-setup"])
