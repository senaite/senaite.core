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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.tests.base import DataTestCase
from bika.lims.utils.analysisrequest import create_analysisrequest as crar
from DateTime import DateTime
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles

try:
    import unittest2 as unittest
except ImportError:  # Python 2.7
    import unittest


class TestAnalysisRequestRetract(DataTestCase):

    def setUp(self):
        super(TestAnalysisRequestRetract, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ["Member", "LabManager"])
        login(self.portal, TEST_USER_NAME)

    def get_services(self):
        query = {
            "portal_type": "AnalysisService",
            "is_active": True,
        }
        return api.search(query)

    def timestamp(self, fmt="%Y-%m-%d"):
        return DateTime().strftime(fmt)

    def create_ar(self):
        client = self.portal.clients["client-1"]
        contacts = client.getContacts()
        contact = contacts[0]
        sampletype = self.portal.bika_setup.bika_sampletypes["sampletype-1"]
        values = {
            "Client": api.get_uid(client),
            "Contact": api.get_uid(contact),
            "DateSampled": self.timestamp(),
            "SampleType": api.get_uid(sampletype)}

        services = self.get_services()[:3]
        service_uids = map(api.get_uid, services)
        return crar(client, self.request, values, service_uids)

    def test_retract_an_analysis_request(self):
        ar = self.create_ar()

        # Check "receive" transition -> sample_received
        api.do_transition_for(ar, "receive")
        self.assertEquals(
            api.get_workflow_status_of(ar, "review_state"),
            "sample_received"
        )

        for analysis in ar.getAnalyses(full_objects=True):
            analysis.setResult("12")

            # Check "submit" transition -> to_be_verified
            api.do_transition_for(analysis, "submit")
            self.assertEquals(
                api.get_workflow_status_of(analysis, "review_state"),
                "to_be_verified"
            )

            # Check "retract" transition -> retracted
            api.do_transition_for(analysis, "retract")
            self.assertEquals(api.get_workflow_status_of(
                analysis, "review_state"), "retracted")

        for analysis in ar.getAnalyses(full_objects=True):
            if api.get_workflow_status_of(
                    analysis, "review_state") == "retracted":
                continue

            # Check "submit" transition -> to_be_verified
            analysis.setResult(12)
            api.do_transition_for(analysis, "submit")
            self.assertEquals(
                api.get_workflow_status_of(analysis, "review_state"),
                "to_be_verified")

        # Check "retract" transition -> "sample_received"
        api.do_transition_for(ar, "retract")
        self.assertEquals(
            api.get_workflow_status_of(ar, "review_state"),
            "sample_received")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAnalysisRequestRetract))
    return suite
