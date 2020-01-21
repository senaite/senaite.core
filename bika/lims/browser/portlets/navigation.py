# -*- coding: utf-8 -*-

from plone.app.portlets.portlets.navigation import Renderer as BaseRenderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class NavigationPortletRenderer(BaseRenderer):
    _template = ViewPageTemplateFile(
        "templates/plone.app.portlets.portlets.navigation.pt")
    recurse = ViewPageTemplateFile(
        "templates/plone.app.portlets.portlets.navigation_recurse.pt")
