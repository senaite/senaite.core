# Testing layer to provide some of the features of PloneTestCase

from bika.lims.exportimport.load_setup_data import LoadSetupData
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import applyProfile
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.testing import z2
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.setuphandlers import setupPortalContent
from Testing.makerequest import makerequest

import Products.ATExtensions
import Products.PloneTestCase.setup
import bika.lims
import collective.js.jqueryui
import transaction
import plone.app.iterate


class BikaTestLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        self.loadZCML(package=Products.ATExtensions)
        self.loadZCML(package=plone.app.iterate)
        self.loadZCML(package=collective.js.jqueryui)
        self.loadZCML(package=bika.lims)

        # Required by Products.CMFPlone:plone-content
        z2.installProduct(app, 'Products.PythonScripts')
        z2.installProduct(app, 'bika.lims')

    def setUpPloneSite(self, portal):
        login(portal.aq_parent, SITE_OWNER_NAME)

        wf = getToolByName(portal, 'portal_workflow')
        wf.setDefaultChain('plone_workflow')
        setupPortalContent(portal)

        # make sure we have folder_listing as a template
        portal.getTypeInfo().manage_changeProperties(
            view_methods=['folder_listing'],
            default_view='folder_listing')

        applyProfile(portal, 'bika.lims:default')

        # Add some test users
        for role in ('LabManager',
                     'LabClerk',
                     'Analyst',
                     'Verifier',
                     'Sampler',
                     'Preserver',
                     'Publisher',
                     'Member',
                     'Reviewer',
                     'RegulatoryInspector'):
            for user_nr in range(2):
                if user_nr == 0:
                    username = "test_%s" % (role.lower())
                else:
                    username = "test_%s%s" % (role.lower(), user_nr)
                member = portal.portal_registration.addMember(
                    username,
                    username,
                    properties={
                        'username': username,
                        'email': username + "@example.com",
                        'fullname': username}
                )
                # Add user to all specified groups
                group_id = role + "s"
                group = portal.portal_groups.getGroupById(group_id)
                if group:
                    group.addMember(username)
                # Add user to all specified roles
                member._addRole(role)
                # If user is in LabManagers, add Owner local role on clients folder
                if role == 'LabManager':
                    portal.clients.manage_setLocalRoles(username, ['Owner', ])

        transaction.commit()

        # load test data
        self.request = makerequest(portal.aq_parent).REQUEST
        self.request.form['setupexisting'] = 1
        self.request.form['existing'] = "test"
        lsd = LoadSetupData(portal, self.request)
        lsd()

        logout()

BIKA_TEST_FIXTURE = BikaTestLayer()

BIKA_INTEGRATION_TESTING = IntegrationTesting(
    bases=(BIKA_TEST_FIXTURE,),
    name="BikaTestingLayer:Integration")

BIKA_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(BIKA_TEST_FIXTURE,),
    name="BikaTestingLayer:Functional")

BIKA_ROBOT_TESTING = FunctionalTesting(
    bases=(BIKA_TEST_FIXTURE, AUTOLOGIN_LIBRARY_FIXTURE, z2.ZSERVER_FIXTURE),
    name="BikaTestingLayer:Robot")
