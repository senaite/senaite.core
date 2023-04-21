# -*- coding: utf-8 -*-

from plone.app.workflow.browser.sharing import SharingView as BaseView
from plone.memoize.instance import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.interfaces import IClient

# Ignore default Plone roles
IGNORE_ROLES = [
    "Reader",
    "Editor",
    "Contributor",
    "Reviewer",
]


class SharingView(BaseView):
    """Custom Sharing View especially for client context
    """
    STICKY = ()
    template = ViewPageTemplateFile("templates/client_sharing.pt")

    def __call__(self):
        # always ensure the client group is visible
        if self.is_client():
            group = self.context.get_group()
            if group:
                self.STICKY += (group.getId(), )
        return super(SharingView, self).__call__()

    def is_client(self):
        """Checks if the current context is a client
        """
        return IClient.providedBy(self.context)

    @memoize
    def roles(self):
        pairs = super(SharingView, self).roles()
        return filter(lambda pair: pair.get("id") not in IGNORE_ROLES, pairs)

    def can_edit_inherit(self):
        return False
