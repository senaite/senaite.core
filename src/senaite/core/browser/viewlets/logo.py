# -*- coding: utf-8 -*-

from plone.app.layout.viewlets.common import ViewletBase
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import ISiteSchema
from Products.CMFPlone.utils import getSiteLogo
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility

LOGO_URL = "++plone++senaite.core.static/images/senaite-site-logo.png"


class LogoViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/logo.pt")

    def update(self):
        super(LogoViewlet, self).update()

        # TODO: should this be changed to settings.site_title?
        self.navigation_root_title = self.portal_state.navigation_root_title()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISiteSchema, prefix="plone", check=False)

        self.logo_title = settings.site_title
        self.logo_width = getattr(settings, "site_logo_width", "200px")
        self.logo_height = getattr(settings, "site_logo_height", "")

        # XXX: Seems that this override fails with Python 2.7
        if getattr(settings, "site_logo", False):
            self.img_src = getSiteLogo()
        else:
            # Get the site logo from the static folder
            self.img_src = "%s/%s" % (self.site_url, LOGO_URL)
