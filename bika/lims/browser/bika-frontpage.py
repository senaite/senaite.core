from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.browser import BrowserView


class FrontPageView(BrowserView):
    template = ViewPageTemplateFile("templates/bika-frontpage.pt")

    def __call__(self):
        self.set_versions()
        self.icon = self.portal_url + "/++resource++bika.lims.images/chevron_big.png"
        return self.template()


    def set_versions(self):
        """Configure a list of product versions from portal.quickinstaller
        """
        self.versions = {}
        qi = self.context.portal_quickinstaller
        for key in qi.keys():
            self.versions[key] = qi.getProductVersion(key)
