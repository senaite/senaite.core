# -*- coding: utf-8 -*-

from cgi import escape

from plone.app.layout.viewlets.common import GlobalSectionsViewlet as Base
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter


class GlobalSectionsDropdownViewlet(Base):
    index = ViewPageTemplateFile("templates/sections_dropdown.pt")

    def update(self):
        super(GlobalSectionsDropdownViewlet, self).update()
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u"plone_portal_state")
        self.navigation_root_url = portal_state.navigation_root_url()
        self.portal_title = escape(
            safe_unicode(portal_state.navigation_root_title()))


class GlobalSectionsViewlet(Base):
    index = ViewPageTemplateFile(
        "templates/plone.app.layout.viewlets.sections.pt")

    def update(self):
        super(GlobalSectionsViewlet, self).update()
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u"plone_portal_state")
        self.navigation_root_url = portal_state.navigation_root_url()
        self.portal_title = escape(
            safe_unicode(portal_state.navigation_root_title()))
