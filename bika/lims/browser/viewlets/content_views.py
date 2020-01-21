# -*- coding: utf-8 -*-

from plone.app.layout.viewlets.common import ContentViewsViewlet as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ContentViewsViewlet(Base):
    index = ViewPageTemplateFile(
        "templates/plone.app.layout.viewlets.contentviews.pt")
