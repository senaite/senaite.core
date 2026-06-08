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
from plone.dexterity.utils import createContent
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import IEditingSchema
from senaite.core.tests.base import BaseTestCase
from senaite.core.upgrade.v02_07_000 import consolidate_laboratory
from zope.component import getUtility


class TestLaboratoryConsolidation(BaseTestCase):
    """Regression tests for the duplicate Laboratory object

    The Laboratory must live as a single DX object at `setup/laboratory`.
    A stale `setup/laboratory-1` and/or a `bika_setup/laboratory` must not
    survive.
    """

    def setUp(self):
        super(TestLaboratoryConsolidation, self).setUp()
        # Disable link-integrity: low-level (un)containment of the setup
        # folder in the test harness fires the linkintegrity retriever on
        # a RequestContainer, which is unrelated to what we test here.
        registry = getUtility(IRegistry)
        editing = registry.forInterface(IEditingSchema, prefix="plone")
        editing.enable_link_integrity_checks = False

    def get_laboratory_ids(self, container):
        return [oid for oid in container.objectIds()
                if api.get_portal_type(container._getOb(oid)) == "Laboratory"]

    def test_profile_creates_single_laboratory_in_setup(self):
        setup = api.get_senaite_setup()
        bika_setup = api.get_bika_setup()

        # exactly one Laboratory, in setup, with the canonical id
        self.assertEqual(self.get_laboratory_ids(setup), ["laboratory"])
        self.assertNotIn("laboratory-1", setup.objectIds())
        self.assertEqual(self.get_laboratory_ids(bika_setup), [])

        # the accessor resolves to the contained DX object
        lab = api.get_senaite_setup().laboratory
        self.assertEqual(api.get_id(lab), "laboratory")
        self.assertEqual(api.get_parent(lab), setup)

    def test_consolidate_keeps_data_lab_and_removes_duplicates(self):
        setup = api.get_senaite_setup()
        bika_setup = api.get_bika_setup()

        # Reproduce the reported state: the data-bearing Laboratory lives
        # in bika_setup (where the old `laboratory` property pointed) and
        # an empty `setup/laboratory-1` was left behind.
        if "laboratory" in setup.objectIds():
            setup._delObject("laboratory")

        data_lab = createContent(
            "Laboratory", id="laboratory", title="My Real Lab")
        bika_setup._setObject("laboratory", data_lab)

        empty_lab = createContent(
            "Laboratory", id="laboratory-1", title="Laboratory")
        setup._setObject("laboratory-1", empty_lab)

        consolidate_laboratory(api.get_tool("portal_setup"))

        # single Laboratory at setup/laboratory holding the real data
        self.assertEqual(self.get_laboratory_ids(setup), ["laboratory"])
        self.assertEqual(self.get_laboratory_ids(bika_setup), [])
        lab = setup._getOb("laboratory")
        self.assertEqual(api.get_title(lab), "My Real Lab")

    def test_consolidate_is_idempotent(self):
        setup = api.get_senaite_setup()

        # already in the consolidated state
        consolidate_laboratory(api.get_tool("portal_setup"))

        self.assertEqual(self.get_laboratory_ids(setup), ["laboratory"])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLaboratoryConsolidation))
    return suite
