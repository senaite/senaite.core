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

    def render(self):
        """Load and render data about current and new versions or pending
        migrations into the session. The session is stored for 24 hours
        between update checks.
        """

        ### First kick out anyone who isn't a manager/labmanager.
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        roles = member.getRoles()
        allowed = 'LabManager' in roles or 'Manager' in roles
        if not allowed:
            return ""

        try:
            sdm = self.context.session_data_manager
            session = sdm.getSessionData(create=True)
        except AttributeError:
            session = {}
        if 'bika-version' not in session.keys():
            session['bika-version'] = {'last-checked': 0}

        # load version data from pypi (possibly refreshed) into var 'pypi'
        now = time.time()
        diff = now - session['bika-version']['last-checked']
        if diff > 86400:
            session['bika-version']['last-checked'] = now
            url = "https://pypi.python.org/pypi/bika.lims/json"
            try:
                jsonstr = urllib.urlopen(url).read()
                session['bika-version']['pypi_info'] = \
                    json.loads(jsonstr)
            except Exception as e:
                logger.info("Failed to retrieve new version info: %s" % e)

        pypi = session['bika-version'].get('pypi_info', None)

        # flag if there is a new pypi release
        # Template vars defined below:
        # - self.has_new_version - true if new pypi version was found.
        # - self.current_version - current bika.lims version on disk
        # - self.new_version - new version number on pypi
        # - self.new_date - date of release on pypi
        versions = {}
        qi = self.context.portal_quickinstaller
        for key in qi.keys():
            versions[key] = qi.getProductVersion(key)
        if pypi:
            self.current_version = versions['bika.lims']
            self.new_version = v = pypi['info']['version']
            self.new_date = pypi['releases'][v][0]['upload_time'].split('T')[0]
            self.has_new_version = v > self.current_version
        else:
            self.has_new_version = False

        # Warn about upgrade steps that have not been run.
        # Variables defined below:
        # - has_upgrade_step: true if profile version in DB is outdated.
        # - qi_info: data from portal_quickinstaller
        qi = self.context.portal_quickinstaller
        self.qi_info = qi.upgradeInfo('bika.lims')
        if self.qi_info['installedVersion'] < self.qi_info['newVersion']:
            self.has_upgrade_step = True
        else:
            self.has_upgrade_step = False

        if self.context.bika_setup.getShowNewReleasesInfo() \
                and (self.has_new_version or self.has_upgrade_step):
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
