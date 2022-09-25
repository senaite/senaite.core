# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.decorators import readonly_transaction
from zope.component import getMultiAdapter
from zope.interface import implementer

from .interfaces import IMenuProvider


@implementer(IMenuProvider)
class MenuProviderView(BrowserView):
    """View to render a menu/submenu
    """
    template = ViewPageTemplateFile('templates/contentmenu.pt')

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.menu = []

    @property
    def contentmenu(self):
        return getMultiAdapter(
            (self.context, self.request, self), name="plone.contentmenu")

    def available(self):
        return self.contentmenu.available()

    @readonly_transaction
    def workflow_menu(self):
        menu_id = "content_status_history"
        menu = self.contentmenu.menu()
        self.menu = filter(
            lambda m: m.get("action").endswith(menu_id), menu)
        return self.template()
