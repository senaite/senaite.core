# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from plone.app.layout.viewlets.common import PersonalBarViewlet
from plone.app.viewletmanager.manager import OrderedViewletManager
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.browser.viewlets.sections import GlobalSectionsViewlet
from zope.component import getMultiAdapter
from zope.component import getUtility

LOGO = "/++plone++senaite.core.static/images/senaite.svg"


class ToolbarViewletManager(OrderedViewletManager):
    custom_template = ViewPageTemplateFile("templates/toolbar.pt")

    def base_render(self):
        return super(ToolbarViewletManager, self).render()

    def render(self):
        return self.custom_template()

    @property
    @memoize
    def context_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name='plone_context_state'
        )

    @property
    @memoize
    def portal_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name='plone_portal_state'
        )

    @memoize
    def is_manager(self):
        tool = getToolByName(self.context, "portal_membership")
        return bool(tool.checkPermission(
            "senaite.core.permissions.ManageBika", aq_inner(self.context)
        ))

    def get_personal_bar(self):
        viewlet = PersonalBarViewlet(
            self.context,
            self.request,
            self.__parent__, self
        )
        viewlet.update()
        return viewlet

    def get_toolbar_logo(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISiteSchema, prefix='senaite', check=False)
        portal_url = self.portal_state.portal_url()
        try:
            logo = settings.toolbar_logo
        except AttributeError:
            logo = LOGO
        if not logo:
            logo = LOGO
        return portal_url + logo

    def get_lims_setup_url(self):
        portal_url = self.portal_state.portal().absolute_url()
        return "/".join([portal_url, "@@lims-setup"])

    def get_global_sections(self):
        viewlet = GlobalSectionsViewlet(
            self.context,
            self.request,
            self.__parent__, self
        )
        viewlet.update()
        return viewlet
