# -*- coding: utf-8 -*-

from plone.app.users.browser.userdatapanel import UserDataPanel as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class UserDataPanel(Base):
    template = ViewPageTemplateFile("templates/account-panel.pt")
