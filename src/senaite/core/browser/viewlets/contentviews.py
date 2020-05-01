# -*- coding: utf-8 -*-

from plone.app.layout.viewlets.common import ContentViewsViewlet as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ContentViewsViewlet(Base):
    index = ViewPageTemplateFile("templates/contentviews.pt")
    menu_template = ViewPageTemplateFile("templates/menu.pt")
