# -*- coding: utf-8 -*-

from plone.app.layout.viewlets.common import PersonalBarViewlet as BaseViewlet


class PersonalBarViewlet(BaseViewlet):
    def update(self):
        super(PersonalBarViewlet, self).update()
