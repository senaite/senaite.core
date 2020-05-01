# -*- coding: utf-8 -*-

from plone.app.layout.viewlets.common import FooterViewlet as Base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class FooterViewlet(Base):
    index = ViewPageTemplateFile("templates/footer.pt")
