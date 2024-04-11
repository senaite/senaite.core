# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import unittest2 as unittest
from bika.lims import api
from bika.lims.utils.analysisrequest import create_analysisrequest
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from senaite.core.tests.base import DataTestCase


class TestHiddenAnalyses(DataTestCase):

    def setUp(self):
        super(TestHiddenAnalyses, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ["Member", "LabManager"])
        login(self.portal, TEST_USER_NAME)
        setup = api.get_senaite_setup()

        servs = self.portal.bika_setup.bika_analysisservices

        # analysis-service-3: Calcium (Ca)
        # analysis-service-6: Cooper (Cu)
        # analysis-service-7: Iron (Fe)
        self.services = [servs["analysisservice-3"],
                         servs["analysisservice-6"],
                         servs["analysisservice-7"]]

        # Calcium - Hidden not set
        # Copper  - Hidden set to False
        self.services[1].setHidden(False)
        # Iron    - Hidden set to True
        self.services[2].setHidden(True)

        profs = setup.analysisprofiles
        # analysisprofile-1: Trace Metals
        self.analysisprofile = profs["analysisprofile-1"]

        sampletemplates = setup.sampletemplates

        # sampletemplate-2: Bruma Metals
        self.sampletemplate = sampletemplates["sampletemplate-2"]
        # reset the services
        self.sampletemplate.setServices(self.services)

    def tearDown(self):
        # Restore
        for s in self.services:
            s.setHidden(False)

        self.analysisprofile.setAnalysisServicesSettings([])
        self.sampletemplate.setAnalysisServicesSettings([])

        super(TestHiddenAnalyses, self).tearDown()

    def test_service_hidden_service(self):
        service = self.services[1]
        self.assertFalse(service.getHidden())
        self.assertFalse(service.Schema().getField("Hidden").get(service))

        service.setHidden(False)
        self.assertFalse(service.getHidden())
        self.assertFalse(service.Schema().getField("Hidden").get(service))

        service.setHidden(True)
        self.assertTrue(service.getHidden())
        self.assertTrue(service.Schema().getField("Hidden").get(service))

        # Restore
        service.setHidden(False)

    def test_service_hidden_profile(self):
        # Profile
        # For Calcium (unset)
        uid = self.services[0].UID()
        self.assertFalse(self.services[0].getHidden())
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertFalse(
            self.analysisprofile.getAnalysisServiceSettings(uid).get("hidden"))

        # For Copper (False)
        uid = self.services[1].UID()
        self.assertFalse(self.services[1].getHidden())
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertFalse(
            self.analysisprofile.getAnalysisServiceSettings(uid).get("hidden"))

        # For Iron (True)
        uid = self.services[2].UID()
        self.assertTrue(self.services[2].getHidden())
        # NOTE: the analysis profile overrides the service setting!
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertFalse(
            self.analysisprofile.getAnalysisServiceSettings(uid).get("hidden"))

        # Modify visibility for Calcium in profile
        uid = self.services[0].UID()
        sets = [{"uid": uid}]
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertFalse(
            self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertFalse(
            self.analysisprofile.getAnalysisServiceSettings(uid).get("hidden"))

        sets = [{"uid": uid, "hidden": False}]
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertFalse(
            self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertFalse(
            self.analysisprofile.getAnalysisServiceSettings(uid).get("hidden"))

        sets = [{"uid": uid, "hidden": True}]
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertTrue(
            self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertTrue(
            self.analysisprofile.getAnalysisServiceSettings(uid).get("hidden"))

        # Modify visibility for Cooper in profile
        uid = self.services[1].UID()
        sets = [{"uid": uid}]
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertFalse(
            self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertFalse(
            self.analysisprofile.getAnalysisServiceSettings(uid).get("hidden"))

        sets = [{"uid": uid, "hidden": False}]
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertFalse(
            self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertFalse(
            self.analysisprofile.getAnalysisServiceSettings(uid).get("hidden"))

        sets = [{"uid": uid, "hidden": True}]
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertTrue(
            self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertTrue(
            self.analysisprofile.getAnalysisServiceSettings(uid).get("hidden"))

        # Modify visibility for Iron in profile
        uid = self.services[2].UID()
        # NOTE: omitted "hidden" defaults to False when set on profile!
        sets = [{"uid": uid}]
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertFalse(
            self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertFalse(
            self.analysisprofile.getAnalysisServiceSettings(uid).get("hidden"))

        sets = [{"uid": uid, "hidden": False}]
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertFalse(
            self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertFalse(
            self.analysisprofile.getAnalysisServiceSettings(uid).get("hidden"))

        sets = [{"uid": uid, "hidden": True}]
        self.analysisprofile.setAnalysisServicesSettings(sets)
        self.assertTrue(
            self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertTrue(
            self.analysisprofile.getAnalysisServiceSettings(uid).get("hidden"))

        # Restore
        self.analysisprofile.setAnalysisServicesSettings([])

    def test_service_hidden_sample_template(self):
        # Template
        # For Calcium (unset)
        uid = self.services[0].UID()
        self.assertFalse(
            self.services[0].getHidden())
        self.assertFalse(
            self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertFalse(
            self.sampletemplate.getAnalysisServiceSettings(uid).get("hidden"))

        # For Copper (False)
        uid = self.services[1].UID()
        self.assertFalse(
            self.services[1].getHidden())
        self.assertFalse(
            self.sampletemplate.isAnalysisServiceHidden(uid))
        self.assertFalse(
            self.sampletemplate.getAnalysisServiceSettings(uid).get("hidden"))

        # For Iron (True)
        uid = self.services[2].UID()
        self.assertTrue(
            self.services[2].getHidden())
        self.assertTrue(
            self.sampletemplate.isAnalysisServiceHidden(uid))
        self.assertTrue(
            self.sampletemplate.getAnalysisServiceSettings(uid).get("hidden"))

        # Modify visibility for Calcium in template
        uid = self.services[0].UID()
        sets = [{"uid": uid}]
        self.sampletemplate.setAnalysisServicesSettings(sets)
        self.assertFalse(
            self.sampletemplate.isAnalysisServiceHidden(uid))
        self.assertFalse(
            self.sampletemplate.getAnalysisServiceSettings(uid).get("hidden"))

        sets = [{"uid": uid, "hidden": False}]
        self.sampletemplate.setAnalysisServicesSettings(sets)
        self.assertFalse(
            self.sampletemplate.isAnalysisServiceHidden(uid))
        self.assertFalse(
            self.sampletemplate.getAnalysisServiceSettings(uid).get("hidden"))

        sets = [{"uid": uid, "hidden": True}]
        self.sampletemplate.setAnalysisServicesSettings(sets)
        self.assertTrue(
            self.sampletemplate.isAnalysisServiceHidden(uid))
        self.assertTrue(
            self.sampletemplate.getAnalysisServiceSettings(uid).get("hidden"))

        # Modify visibility for Cooper in template
        uid = self.services[1].UID()
        sets = [{"uid": uid}]
        self.sampletemplate.setAnalysisServicesSettings(sets)
        self.assertFalse(
            self.sampletemplate.isAnalysisServiceHidden(uid))
        self.assertFalse(
            self.sampletemplate.getAnalysisServiceSettings(uid).get("hidden"))

        sets = [{"uid": uid, "hidden": False}]
        self.sampletemplate.setAnalysisServicesSettings(sets)
        self.assertFalse(
            self.sampletemplate.isAnalysisServiceHidden(uid))
        self.assertFalse(
            self.sampletemplate.getAnalysisServiceSettings(uid).get("hidden"))

        sets = [{"uid": uid, "hidden": True}]
        self.sampletemplate.setAnalysisServicesSettings(sets)
        self.assertTrue(
            self.sampletemplate.isAnalysisServiceHidden(uid))
        self.assertTrue(
            self.sampletemplate.getAnalysisServiceSettings(uid).get("hidden"))

        # Modify visibility for Iron in template
        uid = self.services[2].UID()
        sets = [{"uid": uid, "hidden": False}]
        self.sampletemplate.setAnalysisServicesSettings(sets)
        self.assertFalse(
            self.sampletemplate.isAnalysisServiceHidden(uid))

        self.assertFalse(
            self.sampletemplate.getAnalysisServiceSettings(uid).get("hidden"))

        sets = [{"uid": uid, "hidden": False}]
        self.sampletemplate.setAnalysisServicesSettings(sets)
        self.assertFalse(
            self.sampletemplate.isAnalysisServiceHidden(uid))
        self.assertFalse(
            self.sampletemplate.getAnalysisServiceSettings(uid).get("hidden"))

        sets = [{"uid": uid, "hidden": True}]
        self.sampletemplate.setAnalysisServicesSettings(sets)
        self.assertTrue(
            self.sampletemplate.isAnalysisServiceHidden(uid))
        self.assertTrue(
            self.sampletemplate.getAnalysisServiceSettings(uid).get("hidden"))

        # Restore
        self.sampletemplate.setAnalysisServicesSettings([])

    def test_service_hidden_analysisrequest(self):
        # Input results
        # Client:       Happy Hills
        # SampleType:   Apple Pulp
        # Contact:      Rita Mohale
        # Analyses:     [Calcium, Copper, Iron]
        client = self.portal.clients["client-1"]
        sampletype = self.portal.bika_setup.bika_sampletypes["sampletype-1"]
        request = {}
        services = [s.UID() for s in self.services]
        values = {
            "Client": client.UID(),
            "Contact": client.getContacts()[0].UID(),
            "SamplingDate": "2015-01-01",
            "SampleType": sampletype.UID()}
        ar = create_analysisrequest(client, request, values, services)
        self.assertFalse(
            ar.getAnalysisServiceSettings(services[0]).get("hidden"))
        self.assertFalse(
            ar.isAnalysisServiceHidden(services[0]))
        self.assertFalse(
            ar.getAnalysisServiceSettings(services[1]).get("hidden"))
        self.assertFalse(ar.isAnalysisServiceHidden(services[1]))
        self.assertFalse(
            ar.getAnalysisServiceSettings(services[2]).get("hidden"))
        self.assertTrue(ar.isAnalysisServiceHidden(services[2]))

        # For Calcium (unset)
        uid = self.services[0].UID()
        self.assertFalse(self.services[0].getHidden())
        self.assertFalse(self.analysisprofile.isAnalysisServiceHidden(uid))
        self.assertFalse(
            self.sampletemplate.getAnalysisServiceSettings(uid).get("hidden"))

        # For Copper (False)
        uid = self.services[1].UID()
        self.assertFalse(self.services[1].getHidden())
        self.assertFalse(ar.isAnalysisServiceHidden(uid))
        self.assertFalse("hidden" in ar.getAnalysisServiceSettings(uid))

        # For Iron (True)
        uid = self.services[2].UID()
        self.assertTrue(self.services[2].getHidden())
        self.assertTrue(ar.isAnalysisServiceHidden(uid))
        self.assertFalse("hidden" in ar.getAnalysisServiceSettings(uid))

        # Modify visibility for Calcium in AR
        uid = self.services[0].UID()
        sets = [{"uid": uid}]
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse(ar.isAnalysisServiceHidden(uid))
        self.assertFalse("hidden" in ar.getAnalysisServiceSettings(uid))
        sets = [{"uid": uid, "hidden": False}]
        ar.setAnalysisServicesSettings(sets)
        self.assertFalse(ar.isAnalysisServiceHidden(uid))
        self.assertTrue("hidden" in ar.getAnalysisServiceSettings(uid))
        sets = [{"uid": uid, "hidden": True}]
        ar.setAnalysisServicesSettings(sets)
        self.assertTrue(ar.isAnalysisServiceHidden(uid))
        self.assertTrue("hidden" in ar.getAnalysisServiceSettings(uid))
        ar.setAnalysisServicesSettings([])

        # AR with profile with no changes
        values["Profiles"] = self.analysisprofile.UID()
        ar = create_analysisrequest(client, request, values, services)
        self.assertFalse(ar.getAnalysisServiceSettings(
            services[0]).get("hidden"))
        self.assertFalse(ar.getAnalysisServiceSettings(
            services[1]).get("hidden"))
        self.assertFalse(ar.getAnalysisServiceSettings(
            services[2]).get("hidden"))
        uid = self.services[0].UID()
        self.assertFalse(self.services[0].getHidden())
        self.assertFalse(ar.isAnalysisServiceHidden(uid))
        self.assertFalse(
            ar.getAnalysisServiceSettings(uid).get("hidden"))
        uid = self.services[1].UID()
        self.assertFalse(self.services[1].getHidden())
        self.assertFalse(ar.isAnalysisServiceHidden(uid))
        self.assertFalse(
            ar.getAnalysisServiceSettings(uid).get("hidden"))
        uid = self.services[2].UID()
        self.assertTrue(self.services[2].getHidden())
        self.assertTrue(ar.isAnalysisServiceHidden(uid))

        self.assertFalse(ar.getAnalysisServiceSettings(uid).get("hidden"))

        # AR with template with no changes
        values["Template"] = self.sampletemplate.UID()
        del values["Profiles"]
        ar = create_analysisrequest(client, request, values, services)
        self.assertFalse(
            ar.getAnalysisServiceSettings(services[0]).get("hidden"))
        self.assertFalse(
            ar.getAnalysisServiceSettings(services[1]).get("hidden"))
        # Iron (True)
        self.assertTrue(
            ar.getAnalysisServiceSettings(services[2]).get("hidden"))

        uid = self.services[0].UID()
        self.assertFalse(self.services[0].getHidden())
        self.assertFalse(ar.isAnalysisServiceHidden(uid))
        self.assertFalse(
            ar.getAnalysisServiceSettings(uid).get("hidden"))

        uid = self.services[1].UID()
        self.assertFalse(self.services[1].getHidden())
        self.assertFalse(ar.isAnalysisServiceHidden(uid))
        self.assertFalse(ar.getAnalysisServiceSettings(uid).get("hidden"))

        uid = self.services[2].UID()
        self.assertTrue(self.services[2].getHidden())
        self.assertTrue(ar.isAnalysisServiceHidden(uid))
        self.assertTrue(ar.getAnalysisServiceSettings(uid).get("hidden"))

        # AR with profile, with changes
        values["Profiles"] = self.analysisprofile.UID()
        del values["Template"]
        matrix = [[2, 1, -2],  # AS = Not set
                  [2, 1, -2],  # AS = False
                  [2, 1, -1]]

        for i in range(len(matrix)):
            sets = {"uid": services[i]}
            opts = [0, 1, 2]
            for j in opts:
                if j == 0:
                    sets["hidden"] = False
                elif j == 1:
                    # only for this option we expect the service to return hidden=True!
                    sets["hidden"] = True
                else:
                    # NOTE: omitting this key defaults to False when setting in profile!
                    del sets["hidden"]

                self.analysisprofile.setAnalysisServicesSettings(sets)
                ar = create_analysisrequest(client, request, values, services)
                res = matrix[i][j]

                if res == 1:
                    self.assertTrue(ar.getAnalysisServiceSettings(
                        services[i]).get("hidden"))
                else:
                    self.assertFalse(ar.getAnalysisServiceSettings(
                        services[i]).get("hidden"))

        # Restore
        self.analysisprofile.setAnalysisServicesSettings([])

        # AR with template, with changes
        values["Template"] = self.sampletemplate.UID()
        del values["Profiles"]
        matrix = [[2, 1, -2],  # AS = Not set
                  [2, 1, -2],  # AS = False
                  [2, 1, -1]]
        for i in range(len(matrix)):
            sets = {"uid": services[i]}
            opts = [0, 1, 2]
            for j in opts:
                if j == 0:
                    sets["hidden"] = False
                elif j == 1:
                    sets["hidden"] = True
                else:
                    del sets["hidden"]
                self.sampletemplate.setAnalysisServicesSettings(sets)
                ar = create_analysisrequest(client, request, values, services)
                res = matrix[i][j]
                if abs(res) == 1:
                    self.assertTrue(ar.isAnalysisServiceHidden(services[i]))
                elif abs(res) == 2:
                    self.assertFalse(ar.isAnalysisServiceHidden(services[i]))

        # Restore
        self.sampletemplate.setAnalysisServicesSettings([])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestHiddenAnalyses))
    return suite
