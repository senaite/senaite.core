from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims import logger
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter

class NoSetupDataViewlet(ViewletBase):
    """Alert for instances with no objects in bika_setup_catalog """

    template = ViewPageTemplateFile('templates/load_setup_data_viewlet.pt')

    def render(self):
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        portal_url = portal.absolute_url()
        if self.request.URL == portal_url + "/front-page/document_view" \
           and not bsc():
            self.message = _("No LIMS setup data configured.  "
                             "<a href='load_setup_data'>Click here</a> "
                             "to load pre-configured setup data, or visit "
                             "<a href='@@overview-controlpanel'>Site Setup</a>")
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

class PathBarViewlet(ViewletBase):
    index = ViewPageTemplateFile('templates/path_bar.pt')

    def update(self):
        super(PathBarViewlet, self).update()

        self.is_rtl = self.portal_state.is_rtl()

        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name='breadcrumbs_view')
        self.breadcrumbs = breadcrumbs_view.breadcrumbs()
