# -*- coding: utf-8 -*-

from plone.app.layout.viewlets.globalstatusmessage import \
    GlobalStatusMessage as BaseViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class GlobalStatusMessage(BaseViewlet):
    """Display messages to the current user
    """
    index = ViewPageTemplateFile(
        "templates/plone.app.layout.viewlets.globalstatusmessage.pt")

    def update(self):
        super(GlobalStatusMessage, self).update()
