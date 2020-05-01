# -*- coding: utf-8 -*-

from plone.app.viewletmanager.manager import OrderedViewletManager
from plone.portlets.interfaces import IPortletManager
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletRenderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import navigation
from zope.component import getMultiAdapter
from zope.component import getUtility


class SidebarViewletManager(OrderedViewletManager):
    custom_template = ViewPageTemplateFile("templates/sidebar.pt")

    def base_render(self):
        return super(SidebarViewletManager, self).render()

    def render(self):
        return self.custom_template()

    @property
    @memoize
    def context_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="plone_context_state"
        )

    @property
    @memoize
    def portal_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name="plone_portal_state"
        )

    def render_navigation_portlet(self):
        context = self.context_state.canonical_object()
        view = self.context.restrictedTraverse("@@plone")
        manager = getUtility(
            IPortletManager, name="plone.leftcolumn", context=context)
        assignment = navigation.Assignment(topLevel=0)
        renderer = getMultiAdapter(
            (self.context, self.request, view, manager, assignment),
            IPortletRenderer)
        return renderer.render()
