from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView


class FrontPageView(BrowserView):
    template = ViewPageTemplateFile("templates/bika-frontpage.pt")

    def __call__(self):
        todashboard = False
        mtool=getToolByName(self.context, 'portal_membership')
        if not mtool.isAnonymousUser() and self.context.bika_setup.getDashboardByDefault():
            # If authenticated user with labman role,
            # display the Main Dashboard view
            pm = getToolByName(self.context, "portal_membership")
            member = pm.getAuthenticatedMember()
            roles = member.getRoles()
            todashboard = 'Manager' in roles or 'LabManager' in roles

        if todashboard == True:
            self.request.response.redirect(self.portal_url + "/bika-dashboard")
        else:
            self.set_versions()
            self.icon = self.portal_url + "/++resource++bika.lims.images/chevron_big.png"
            return self.template()


    def set_versions(self):
        """Configure a list of product versions from portal.quickinstaller
        """
        self.versions = {}
        self.upgrades = {}
        qi = self.context.portal_quickinstaller
        for key in qi.keys():
            info = qi.upgradeInfo('bika.lims')
            self.versions[key] = qi.getProductVersion(key)
            info = qi.upgradeInfo(key)
            if info and 'installedVersion' in info:
                self.upgrades[key] = info['installedVersion']
