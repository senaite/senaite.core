# -*- coding: utf-8 -*-

from plone.app.layout.viewlets.common import GlobalSectionsViewlet as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class GlobalSectionsViewlet(Base):
    index = ViewPageTemplateFile("templates/sections.pt")
