# -*- coding: utf-8 -*-

from plone.app.layout.viewlets.common import LogoViewlet as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class LogoViewlet(Base):
    index = ViewPageTemplateFile(
        "templates/plone.app.layout.viewlets.logo.pt")

    def update(self):
        super(Base, self).update()

        portal = self.portal_state.portal()
        bprops = portal.restrictedTraverse("base_properties", None)
        if bprops is not None:
            logoName = bprops.logoName
        else:
            logoName = "logo.jpg"

        logoTitle = self.portal_state.portal_title()
        self.logo_tag = portal.restrictedTraverse(logoName).tag(
            title=logoTitle, alt=logoTitle, scale=0.5)
        self.navigation_root_title = self.portal_state.navigation_root_title()
