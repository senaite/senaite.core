# -*- coding: utf-8 -*-

from bika.lims import senaiteMessageFactory as _
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class RemarksViewlet(ViewletBase):
    """Viewlet for remarks field
    """
    index = ViewPageTemplateFile("templates/remarks.pt")

    title = _("Remarks")
    icon_name = "remarks"

    def available(self):
        return True
