# This file is part of Bika LIMS
#
# Copyright 2011-2016 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase


class DocumentActionsViewlet(ViewletBase):
    """Overload the default to print pretty icons
    """

    index = ViewPageTemplateFile("templates/document_actions.pt")

    def render(self):
        portal_factory = getToolByName(self.context, 'portal_factory')
        if portal_factory.isTemporary(self.context):
            return self.index()
        self.actions = []
        portal_actions = getToolByName(self.context, 'portal_actions')
        actions = portal_actions.listFilteredActionsFor(self.context)
        if 'document_actions' in actions:
            for action in actions['document_actions']:
                self.actions.append(action)
        return self.index()
