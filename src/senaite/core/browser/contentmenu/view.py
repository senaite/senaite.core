# -*- coding: utf-8 -*-

from plone.app.contentmenu.view import ContentMenuProvider as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ContentMenuProvider(Base):
    """Content menu provider for the "view" tab: displays the menu
    """
    index = ViewPageTemplateFile('templates/contentmenu.pt')
