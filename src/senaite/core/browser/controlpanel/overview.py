# -*- coding: utf-8 -*-

from Products.CMFPlone.controlpanel.browser.overview import \
    OverviewControlPanel as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class OverviewControlPanel(Base):
    template = ViewPageTemplateFile("templates/overview.pt")
