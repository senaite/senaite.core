# -*- coding: utf-8 -*-

from plone.app.layout.viewlets.common import SiteActionsViewlet as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SiteActionsViewlet(Base):
    index = ViewPageTemplateFile("templates/site_actions.pt")
