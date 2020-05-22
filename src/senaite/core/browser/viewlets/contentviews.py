# -*- coding: utf-8 -*-

from plone.app.layout.viewlets.common import ContentViewsViewlet as Base
from plone.memoize.view import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter


class ContentViewsViewlet(Base):
    index = ViewPageTemplateFile("templates/contentviews.pt")
    menu_template = ViewPageTemplateFile("templates/menu.pt")

    @property
    @memoize
    def context_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="plone_context_state")

    def is_action_selected(self, action):
        """Workaround for dysfunctional `selected` attribute in action
        """
        action_url = action.get('url')
        if not action_url:
            return action.get("selected", False)
        base_url = action_url.split("?")[0]
        return base_url == self.context_state.current_base_url()
