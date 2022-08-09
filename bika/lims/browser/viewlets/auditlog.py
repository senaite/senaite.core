# -*- coding: utf-8 -*-

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
