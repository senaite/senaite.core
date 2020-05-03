# -*- coding: utf-8 -*-

from plone.app.layout.viewlets.content import DocumentActionsViewlet as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class DocumentActionsViewlet(Base):
    index = ViewPageTemplateFile("templates/documentactions.pt")
