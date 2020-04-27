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

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import api
from plone.app.layout.viewlets.common import ViewletBase


class AttachmentsViewlet(ViewletBase):
    """Viewlet to manage Attachments in ARs

    Most of the heavy lifting is now delegated in the template to the
    `attachments_view` browser view.
    """
    template = ViewPageTemplateFile("templates/attachments.pt")

    def get_attachments_view(self):
        # refactored functionality into this separate Browser view, to be able
        # to have a form submit target.
        attachments_view = api.get_view("attachments_view",
                                        context=self.context,
                                        request=self.request)
        return attachments_view

    def show(self):
        """Controls if the viewlet should be rendered
        """
        url = self.request.getURL()
        # XXX: Hack to show the viewlet only on the AR base_view
        if not any(map(url.endswith, ["base_view", "manage_results"])):
            return False
        return self.attachments_view.user_can_add_attachments() or \
               self.attachments_view.user_can_update_attachments()

    def update(self):
        """Called always before render()
        """
        super(AttachmentsViewlet, self).update()
        self.attachments_view = self.get_attachments_view()

    def render(self):
        if not self.show():
            return ""
        return self.template()


class WorksheetAttachmentsViewlet(AttachmentsViewlet):
    """Viewlet to manage Attachments on Worksheets

    Most of the heavy lifting is now delegated in the template to the
    `attachments_view` browser view.
    """
    template = ViewPageTemplateFile("templates/worksheet_attachments.pt")

    def show(self):
        """Controls if the viewlet should be rendered
        """
        # XXX: Hack to show the viewlet only on the WS manage_results view
        if not self.request.getURL().endswith("manage_results"):
            return False
        return True

    def get_services(self):
        """Returns a list of AnalysisService objects
        """
        return self.context.getWorksheetServices()
