# -*- coding: utf-8 -*-

from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ResourcesViewlet(ViewletBase):
    """This viewlet inserts static resources on page header.
    """
    index = ViewPageTemplateFile("../static/resources.pt")
