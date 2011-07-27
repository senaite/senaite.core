from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import logger
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter

#class MyViewlet(ViewletBase):
#    render = ViewPageTemplateFile('viewlet.pt')
#
#    def update(self):
#        self.computed_value = 'any output'

class DocumentActionsViewlet(ViewletBase):
    """Overload the default to print pretty icons """

    index = ViewPageTemplateFile("document_actions.pt")

    def render(self):
        self.actions = []
        portal_actions = getToolByName(self.context, 'portal_actions')
        actions = portal_actions.listFilteredActionsFor(self.context)
        if 'document_actions' in actions:
            for action in actions['document_actions']:
                self.actions.append(action)
        return self.index()
