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

from bika.lims import AddAttachment
from bika.lims import api
from bika.lims import FieldEditAnalysisResult
from bika.lims import WorksheetAddAttachment
from bika.lims.api.security import check_permission
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize import view
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


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
        return True

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
        return check_permission(WorksheetAddAttachment, self.context)

    @view.memoize
    def get_services(self):
        """Returns a list of dicts that represent the Analysis Services that
        are editable and present in current Worksheet
        """
        services = set()
        for analysis in self.context.getAnalyses():
            # Skip non-editable analyses
            if not check_permission(FieldEditAnalysisResult, analysis):
                continue
            service = analysis.getAnalysisService()
            services.add(service)

        # Return the
        services = sorted(list(services), key=lambda s: api.get_title(s))
        return map(self.get_service_info, services)

    def get_service_info(self, service):
        """Returns a dict that represents an analysis service
        """
        return {
            "uid": api.get_uid(service),
            "title": api.get_title(service),
        }
