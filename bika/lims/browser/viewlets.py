import json
import urllib
import time

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter
from bika.lims import logger


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


class NewVersionsViewlet(ViewletBase):
    """ Handle notifications related to new version of Bika LIMS

    1) Check pypi for new version
    2) Check prefs to see if upgrade steps are required.

    """

    index = ViewPageTemplateFile("templates/new_version.pt")

    def get_versions(self):
        """Configure self.versions, a list of product versions
        from portal.quickinstaller
        """
        self.versions = {}
        qi = self.context.portal_quickinstaller
        for key in qi.keys():
            self.versions[key] = qi.getProductVersion(key)

    def check_new_version(self):
        """Look for new updates at pypi
        """
        self.current_version = self.versions['bika.lims']
        if not self.current_version:
            self.has_new_version = False
            return
        url = "https://pypi.python.org/pypi/bika.lims/json"
        try:
            jsonstr = urllib.urlopen(url).read()
            self.pypi = json.loads(jsonstr)
            v = self.new_version = self.pypi['info']['version']
            self.new_date = \
                self.pypi['releases'][v][0]['upload_time'].split('T')[0]
        except Exception as e:
            logger.info("Failed to retrieve new version info: %s" % e)
            v = self.current_version
            self.new_date = ""
        self.has_new_version = v > self.current_version

    def check_new_upgrade_step(self):
        """Warn about upgrade steps that have not been run.  This will override
        the users choice in settings: un-executed upgrade steps are always
        alerted.
        """
        qi = self.context.portal_quickinstaller
        self.info = qi.upgradeInfo('bika.lims')
        if self.info['installedVersion'] < self.info['newVersion']:
            self.has_upgrade_step = True
        else:
            self.has_upgrade_step = False

    def check_session(self):
        """Return False if the session hint claims that we already checked.
        Return True if the session has no record, or if more than one day has
        passed since we last checked.
        """
        et = time.time()
        try:
            sdm = self.context.session_data_manager
        except AttributeError:
            # While testing, the session data manager is not yet instantiated.
            return False
        session = sdm.getSessionData(create=True)
        diff = et - session.get('bika.lims-version-check', et)
        if diff > 86400 or diff == 0:
            session['bika.lims-version-check'] = et
            return True
        else:
            return False

    def render(self):
        if not self.check_session():
            return ""

        self.get_versions()
        self.check_new_version()
        self.check_new_upgrade_step()

        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        allowed = 'LabManager' in roles or 'Manager' in roles

        if allowed \
                and self.context.bika_setup.getShowNewReleasesInfo() \
                and self.has_new_version:
            return self.index()
        elif allowed and self.has_upgrade_step:
            return self.index()
        else:
            return ""

class PathBarViewlet(ViewletBase):
    index = ViewPageTemplateFile('templates/path_bar.pt')

    def update(self):
        super(PathBarViewlet, self).update()

        self.is_rtl = self.portal_state.is_rtl()

        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name='breadcrumbs_view')
        self.breadcrumbs = breadcrumbs_view.breadcrumbs()


class AuthenticatorViewlet(ViewletBase):
    index = ViewPageTemplateFile('templates/authenticator.pt')

