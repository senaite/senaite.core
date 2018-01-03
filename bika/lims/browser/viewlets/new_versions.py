# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

import json
import time
import urllib

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import logger
from plone.app.layout.viewlets.common import ViewletBase


class NewVersionsViewlet(ViewletBase):
    """ Handle notifications related to new version of Bika LIMS

    1) Check pypi for new version
    2) Check prefs to see if upgrade steps are required.

    """

    index = ViewPageTemplateFile("templates/new_versions.pt")

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
