# -*- coding: utf-8 -*-

from plone.app.layout.viewlets.common import SiteActionsViewlet as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SiteActionsViewlet(Base):
    index = ViewPageTemplateFile(
        "templates/plone.app.layout.viewlets.site_actions.pt")
