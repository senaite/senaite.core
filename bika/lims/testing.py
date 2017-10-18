from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from Products.CMFCore.utils import getToolByName
from plone.app.testing import login
from plone.app.testing import logout
from Products.CMFPlone.setuphandlers import setupPortalContent


class BikaLIMSLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import bika.lims
        self.loadZCML(package=bika.lims)

        # Install product and call its initialize() function
        z2.installProduct(app, 'bika.lims')

    def setUpPloneSite(self, portal):
        # login(portal.aq_parent, 'admin')
        #
        # wf = getToolByName(portal, 'portal_workflow')
        # wf.setDefaultChain('plone_workflow')
        # setupPortalContent(portal)

        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'bika.lims:default')

        # # make sure we have folder_listing as a template
        # portal.getTypeInfo().manage_changeProperties(
        #     view_methods=['folder_listing'],
        #     default_view='folder_listing')
        #
        # # Add some test users
        # for role in (
        #         'LabManager',
        #         'LabClerk',
        #         'Analyst',
        #         'Verifier',
        #         'Sampler',
        #         'Preserver',
        #         'Publisher',
        #         'Member',
        #         'Reviewer',
        #         'RegulatoryInspector'):
        #     for user_nr in range(2):
        #         if user_nr == 0:
        #             username = "test_%s" % (role.lower())
        #         else:
        #             username = "test_%s%s" % (role.lower(), user_nr)
        #         try:
        #             member = portal.portal_registration.addMember(
        #                 username,
        #                 username,
        #                 properties={
        #                     'username': username,
        #                     'email': username + "@example.com",
        #                     'fullname': username
        #                 }
        #             )
        #             # Add user to all specified groups
        #             group_id = role + "s"
        #             group = portal.portal_groups.getGroupById(group_id)
        #
        #             if group:
        #                 group.addMember(username)
        #                 # Add user to all specified roles
        #             member._addRole(role)
        #             # If user is in LabManagers, add Owner local role on
        #             # clients folder
        #             if role == 'LabManager':
        #                 portal.clients.manage_setLocalRoles(
        #                     username, ['Owner', ])
        #         except ValueError:
        #             pass  # user exists
        # logout()

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'bika.lims')


BIKA_LIMS_FIXTURE = BikaLIMSLayer()
BIKA_LIMS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(BIKA_LIMS_FIXTURE,), name="BikaLIMSLayer:Functional")
