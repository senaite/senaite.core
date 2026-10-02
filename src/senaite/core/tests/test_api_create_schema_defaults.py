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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from plone.app.linkintegrity.retriever import DXGeneral
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from senaite.core.tests.base import BaseTestCase
from senaite.core.upgrade.utils import temporary_allow_type


class TestAPICreateSchemaDefaults(BaseTestCase):
    """api.create must initialize DX schema fields so the object is fully
    formed before ObjectAddedEvent fires (regression for the link
    integrity retriever crashing on unset RichText fields during site
    creation).
    """

    def setUp(self):
        super(TestAPICreateSchemaDefaults, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def create_setup(self, obj_id):
        with temporary_allow_type(self.portal, "Setup"):
            return api.create(
                self.portal, "Setup", id=obj_id, title="Test Setup")

    def test_richtext_field_is_initialized_on_create(self):
        setup = self.create_setup("setup_init")
        # the RichText field must be a real instance attribute, so a raw
        # getattr does not fall through acquisition to the request
        # container
        self.assertIn("email_body_sample_publication", setup.__dict__)

    def test_link_integrity_retriever_does_not_crash(self):
        # This reproduces the exact path that broke site creation: the
        # link integrity retriever reads the RichText fields of the newly
        # added object via a raw getattr.
        setup = self.create_setup("setup_links")
        retriever = DXGeneral(setup)
        # must not raise AttributeError
        links = retriever.retrieveLinks()
        self.assertIsInstance(links, set)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAPICreateSchemaDefaults))
    return suite
