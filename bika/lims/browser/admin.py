from Products.CMFPlone.browser.admin import Overview as OverviewBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile



class Overview(OverviewBase):
    """ Customized plone overview. """

    index = ViewPageTemplateFile('templates/plone-overview.pt')

    def __call__(self):
        """ Redirect to bika.lims instance if single instance is found. """
        sites = self.sites()
        if len(sites) == 1 and not self.outdated(sites[0]):
            return self.request.response.redirect(sites[0].absolute_url())
        return self.index()
