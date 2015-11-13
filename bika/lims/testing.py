# Testing layer to provide some of the features of PloneTestCase
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, \
    setSecurityManager
from Products.CMFPlone.utils import _createObjectByType
from plone.app.robotframework import AutoLogin, Content
from zope.component.hooks import getSite
from bika.lims import logger
from bika.lims.exportimport.load_setup_data import LoadSetupData
from bika.lims.utils.analysisrequest import create_analysisrequest
from plone import api
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.robotframework.remote import RemoteLibrary, RemoteLibraryLayer
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import SITE_OWNER_NAME
from plone.testing import z2
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.setuphandlers import setupPortalContent
from Testing.makerequest import makerequest
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.z2 import Browser

import bika.lims
import pkg_resources
import collective.js.jqueryui
import plone.app.iterate
import Products.ATExtensions
import Products.PloneTestCase.setup

import transaction


class SimpleTestLayer(PloneSandboxLayer):
    """Configure a default site with bika.lims addon installed,
    and with no data or settings loaded.
    """
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
                try:
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
                        portal.clients.manage_setLocalRoles(username,
                                                            ['Owner', ])
                except ValueError:
                    pass  # user exists

        # Force the test browser to show the site always in 'en'
        ltool = portal.portal_languages
        ltool.manage_setLanguageSettings('en', ['en'],
                                         setUseCombinedLanguageCodes=False,
                                         startNeutral=True)

        logout()


def getBrowser(portal, loggedIn=True, username=TEST_USER_NAME,
               password=TEST_USER_PASSWORD):
    """Instantiate and return a testbrowser for convenience
    This is done weirdly because I could not figure out how else to
    pass the browser to the doctests"""
    browser = Browser(portal)
    browser.addHeader('Accept-Language', 'en')
    browser.handleErrors = False
    if loggedIn:
        browser.open(portal.absolute_url())
        browser.getControl('Login Name').value = username
        browser.getControl('Password').value = password
        browser.getControl('Log in').click()
        assert ('You are now logged in' in browser.contents)
    return browser


BIKA_SIMPLE_FIXTURE = SimpleTestLayer()
BIKA_SIMPLE_FIXTURE['getBrowser'] = getBrowser
BIKA_SIMPLE_TESTING = FunctionalTesting(
    bases=(BIKA_SIMPLE_FIXTURE,),
    name="SimpleTestingLayer:Functional"
)


class BikaTestLayer(SimpleTestLayer):
    def setUpZope(self, app, configurationContext):
        super(BikaTestLayer, self).setUpZope(app, configurationContext)

    def setUpPloneSite(self, portal):
        super(BikaTestLayer, self).setUpPloneSite(portal)

        login(portal.aq_parent, SITE_OWNER_NAME)  # again

        # load test data
        self.request = makerequest(portal.aq_parent).REQUEST
        self.request.form['setupexisting'] = 1
        self.request.form['existing'] = "bika.lims:test"
        lsd = LoadSetupData(portal, self.request)
        lsd()

        logout()


class Keywords(object):
    """Robot Framework keyword library
    """

    def resource_filename(self):
        res = pkg_resources.resource_filename("bika.lims", "tests")
        return res


class RemoteKeywords(Keywords, RemoteLibrary):


    def write_at_field_values(self, obj, **kwargs):
        """Write valid field values from kwargs into the object's AT fields.
        """
        uc = getToolByName(obj, 'uid_catalog')
        schema = obj.Schema()
        # fields contains all schema-valid field values from the request.
        fields = {}
        for fieldname, value in kwargs.items():
            if fieldname not in schema:
                continue
            field = schema.getField(fieldname)
            fieldtype = field.getType()
            mutator = field.getMutator(obj)
            if schema[fieldname].type in ('reference'):
                # Assume that the value is a UID
                brains = uc(UID=value)
                if not brains:
                    logger.warn("Can't resolve: %s:%s" % (fieldname, value))
                    continue
                if schema[fieldname].multiValued:
                    value = [b.UID for b in brains] if brains else []
                else:
                    value = brains[0].UID if brains else None
            elif fieldtype == 'Products.Archetypes.Field.BooleanField':
                if value.lower() in ('0', 'false', 'no') or not value:
                    value = False
                else:
                    value = True
            elif fieldtype in [
                'Products.ATExtensions.field.records.RecordsField',
                'Products.ATExtensions.field.records.RecordField']:
                value = eval(value)
            if mutator:
                mutator(value)
            else:
                field.set(obj, value)
        obj.reindexObject()

    def create_object(self, path, portal_type, id, **kwargs):
        portal = api.portal.get()
        container = portal.restrictedTraverse(path.strip('/').split('/'))
        # create object
        obj = _createObjectByType(portal_type, container, id, **kwargs)
        obj.processForm(container.REQUEST, values=kwargs)
        self.write_at_field_values(obj, **kwargs)
        return obj.UID()

    def get_uid(self, catalog_name, **query):
        portal = api.portal.get()
        catalog = getToolByName(portal, catalog_name)
        # catalog call
        brains = catalog(**query)
        if brains:
            return brains[0].UID
        logger.warning("No brain in %s for %s" % (catalog_name, query))

    def create_ar(self, path, analyses=[], **kwargs):
        portal = api.portal.get()
        container = portal.restrictedTraverse(path.strip('/').split('/'))
        # create object
        obj = create_analysisrequest(container, container.REQUEST,
                                     kwargs, analyses)
        return obj.UID()

# BIKA_SIMPLE_FIXTURE = FunctionalTesting(
#     bases=(BIKA_SIMPLE_FIXTURE,),
#     name="BikaSimple:Functional")

BIKA_FUNCTIONAL_FIXTURE = BikaTestLayer()
BIKA_FUNCTIONAL_FIXTURE['getBrowser'] = getBrowser
BIKA_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(BIKA_FUNCTIONAL_FIXTURE,),
    name="BikaTestingLayer:Functional"
)

REMOTE_FIXTURE = RemoteLibraryLayer(
    libraries=(AutoLogin, Content, RemoteKeywords,),
    name="RemoteLibrary:RobotRemote"
)

BIKA_ROBOT_TESTING = FunctionalTesting(
    bases=(BIKA_FUNCTIONAL_FIXTURE,
           REMOTE_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name="BikaTestingLayer:Robot"
)
