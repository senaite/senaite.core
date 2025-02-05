# -*- coding: utf-8 -*-

from bika.lims.interfaces import IReceived
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class NotSampledViewlet(ViewletBase):
    """Print a viewlet to display a message stating the Sample cannot
    transition due to an unset DateSampled
    """
    index = ViewPageTemplateFile("templates/not_sampled.pt")

    def is_visible(self):
        """Returns whether this viewlet must be visible or not
        """
        sample = self.context
        if IReceived.providedBy(sample):
            # sample already received
            return False
        return not sample.getDateSampled()
