# -*- coding: utf-8 -*-

from plone.app.layout.viewlets.common import PersonalBarViewlet as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PersonalBarViewlet(Base):
    index = ViewPageTemplateFile(
        "templates/plone.app.layout.viewlets.personal_bar.pt")
