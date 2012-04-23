from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter

#class MyViewlet(ViewletBase):
#    render = ViewPageTemplateFile('viewlet.pt')
#
#    def update(self):
#        self.computed_value = 'any output'

class NoSetupDataViewlet(ViewletBase):
    """Alert for instances with no objects in bika_setup_catalog """
    template = ViewPageTemplateFile('templates/load_setup_data_viewlet.pt')
    def render(self):
        bsc = getToolByName(self, 'bika_setup_catalog')
        # I should be able to register this with something like IPloneSiteRoot
        # in the zcml, but that didn't work.
        # for the moment at least, this if statement works well enough.
        if not self.request.URL.endswith('load_setup_data') \
           and not self.request.URL.endswith('overview-controlpanel') \
           and not self.request.URL.find('bika_setup') > -1 \
           and not bsc():
            self.message = _("No LIMS setup data configured.  <a href='load_setup_data'>Click here</a> to load pre-configured setup data, or visit <a href='@@overview-controlpanel'>Site Setup</a>")
            return self.template()
        return ''

class DocumentActionsViewlet(ViewletBase):
    """Overload the default to print pretty icons """

    index = ViewPageTemplateFile("templates/document_actions.pt")

    def render(self):
        self.actions = []
        portal_actions = getToolByName(self.context, 'portal_actions')
        actions = portal_actions.listFilteredActionsFor(self.context)
        if 'document_actions' in actions:
            for action in actions['document_actions']:
                self.actions.append(action)
        return self.index()
