# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.permissions import AddAnalysisRequest
from plone.app.layout.viewlets import ViewletBase
from plone.memoize.instance import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.interfaces import ISamplesView
from zope.component import getMultiAdapter


class AddSamplesViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/add_samples.pt")

    def available(self):
        """Check if the add samples viewlet should be rendered
        """
        if not ISamplesView.providedBy(self.view):
            return False
        if not api.security.check_permission(AddAnalysisRequest, self.context):
            return False
        return True

    def get_sample_add_number(self):
        """Return the default number of Samples to add
        """
        setup = api.get_setup()
        return setup.getDefaultNumberOfARsToAdd() or 1

    def get_add_url(self):
        """Return the sample add URL
        """
        return "{}/ar_add".format(api.get_url(self.context))

    @property
    @memoize
    def theme_view(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="senaite_theme")
