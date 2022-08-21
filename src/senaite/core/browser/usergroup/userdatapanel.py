# -*- coding: utf-8 -*-

from plone.app.users.browser.userdatapanel import UserDataConfiglet as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class UserDataConfiglet(Base):
    """Control panel version of the userdata panel
    """
    template = ViewPageTemplateFile("templates/account-configlet.pt")
