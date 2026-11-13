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

import logging
import unittest

from bika.lims import api
from plone.registry import field
from plone.registry.interfaces import IRegistry
from plone.registry.record import Record
from senaite.core.tests.base import BaseTestCase
from senaite.core.upgrade.v02_07_000 import migrate_analysis_columns_to_setup
from zope.component import getUtility

# The record of an earlier version a site still has, although its field is
# no longer part of the interface
FORMER_RECORD = ("senaite.core.registry.schema.ISampleViewRegistry"
                 ".sampleview_analysis_columns_order")


class CollectErrors(logging.Handler):
    """Collects the messages of the errors logged
    """

    def __init__(self):
        logging.Handler.__init__(self, level=logging.ERROR)
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


class TestMigrateAnalysisColumns(BaseTestCase):
    """The upgrade step moves the columns order from the registry to setup
    """

    def setUp(self):
        super(TestMigrateAnalysisColumns, self).setUp()
        self.errors = CollectErrors()
        logging.getLogger("senaite.core").addHandler(self.errors)

    def tearDown(self):
        logging.getLogger("senaite.core").removeHandler(self.errors)
        super(TestMigrateAnalysisColumns, self).tearDown()

    def test_site_without_former_records(self):
        setup = api.get_senaite_setup()
        before = setup.getSampleviewAnalysisColumnsOrder()

        migrate_analysis_columns_to_setup(self.portal.portal_setup)

        # nothing to migrate is no error
        self.assertEqual(self.errors.messages, [])
        self.assertEqual(setup.getSampleviewAnalysisColumnsOrder(), before)

    def test_site_with_former_record(self):
        registry = getUtility(IRegistry)
        registry.records[FORMER_RECORD] = Record(
            field.List(value_type=field.TextLine()), [u"Result", u"Method"])

        migrate_analysis_columns_to_setup(self.portal.portal_setup)

        columns = api.get_senaite_setup().getSampleviewAnalysisColumnsOrder()
        self.assertEqual(list(columns[:2]), [u"Result", u"Method"])
        self.assertEqual(self.errors.messages, [])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMigrateAnalysisColumns))
    return suite
