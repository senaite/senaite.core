# -*- coding: utf-8 -*-

from plone.app.layout.links.viewlets import FaviconViewlet as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class FaviconViewlet(Base):
    _template = ViewPageTemplateFile("templates/favicon.pt")
