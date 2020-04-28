# -*- coding: utf-8 -*-

from plone.app.layout.viewlets.common import PersonalBarViewlet as BaseViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PersonalBarViewlet(BaseViewlet):
    index = ViewPageTemplateFile(
        "templates/plone.app.layout.viewlets.anontools.pt")

    def update(self):
        super(PersonalBarViewlet, self).update()
