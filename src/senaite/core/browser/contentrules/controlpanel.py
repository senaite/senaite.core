# -*- coding: utf-8 -*-

from plone.app.contentrules.browser.controlpanel import \
    ContentRulesControlPanel as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ContentRulesControlPanel(Base):
    """Manage rules in a the global rules container
    """
    template = ViewPageTemplateFile("templates/controlpanel.pt")
