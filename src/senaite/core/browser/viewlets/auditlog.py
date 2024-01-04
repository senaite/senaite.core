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
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AuditlogDisabledViewlet(ViewletBase):
    """Viewlet that is displayed when the Auditlog is disabled
    """
    template = ViewPageTemplateFile("templates/auditlog_disabled.pt")

    def __init__(self, context, request, view, manager=None):
        super(AuditlogDisabledViewlet, self).__init__(
            context, request, view, manager=manager)
        self.context = context
        self.request = request
        self.view = view

    @property
    def setup(self):
        return api.get_setup()

    def get_setup_url(self):
        """Return the absolute URL of the setup
        """
        return api.get_url(self.setup)

    def is_enabled(self):
        """Returns whether the global auditlog is disabled
        """
        return self.setup.getEnableGlobalAuditlog()

    def is_disabled(self):
        """Returns whether the global auditlog is disabled
        """
        return not self.is_enabled()

    def index(self):
        if self.is_enabled():
            return ""
        return self.template()
