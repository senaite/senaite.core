# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
