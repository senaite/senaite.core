# -*- coding: utf-8 -*-

from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ColophonViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/colophon.pt")
