# -*- coding: utf-8 -*-

from plone.app.contentrules.browser.elements import ManageElements as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ManageElements(Base):
    """Manage elements in a rule
    """
    template = ViewPageTemplateFile('templates/manage-elements.pt')
