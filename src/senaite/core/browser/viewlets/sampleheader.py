# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SampleHeaderViewlet(ViewletBase):
    """Header table with editable sample fields
    """
    template = ViewPageTemplateFile("templates/sampleheader.pt")

    def render(self):
        return self.template()
