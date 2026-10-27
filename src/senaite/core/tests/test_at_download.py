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
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from senaite.core.tests.base import BaseTestCase
from six import StringIO
from zExceptions import NotFound
from zope.component import getMultiAdapter


class TestATDownload(BaseTestCase):
    """`at_download` is acquired site-wide from Products.Archetypes and
    raises an AttributeError on content without an Archetypes schema, which
    surfaces as a 500 with a rendered traceback for managers. The view
    registered by senaite.core shadows it and answers with a 404 instead.
    """

    def setUp(self):
        super(TestATDownload, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def get_view(self, context, fieldname=None):
        view = getMultiAdapter((context, self.request), name="at_download")
        if fieldname is not None:
            view = view.publishTraverse(self.request, fieldname)
        return view

    def test_view_shadows_the_archetypes_skin_script(self):
        # the view must be the one from senaite.core, not the skin script
        view = self.get_view(self.portal)
        self.assertEqual(type(view).__name__, "ATDownloadView")

    def test_field_name_is_taken_from_the_subpath(self):
        view = self.get_view(self.portal, "SomeField")
        self.assertEqual(view.traverse_subpath, ["SomeField"])

    def test_not_found_on_dexterity_content(self):
        setup = api.get_senaite_setup()
        self.assertTrue(api.is_dexterity_content(setup))
        self.assertRaises(NotFound, self.get_view(setup))

    def test_not_found_on_portal_root(self):
        self.assertRaises(NotFound, self.get_view(self.portal))

    def test_not_found_on_unknown_field(self):
        setup = api.get_senaite_setup()
        self.assertRaises(NotFound, self.get_view(setup, "NoSuchField"))

    def create_attachment(self):
        client = api.create(self.portal.clients, "Client",
                            Name="Happy Hills", ClientID="HH")
        attachment = api.create(client, "Attachment")
        attachment_file = StringIO("hello")
        attachment_file.filename = "senaite.txt"
        attachment.setAttachmentFile(attachment_file)
        return attachment

    def test_downloads_archetypes_field(self):
        # regression: the legitimate case must keep working
        attachment = self.create_attachment()
        view = self.get_view(attachment, "AttachmentFile")
        self.assertEqual(view.get_field().getName(), "AttachmentFile")
        self.assertIsNotNone(view())

    def test_not_found_without_primary_field(self):
        # Attachment declares no primary field, so there is nothing to
        # resolve without an explicit field name. The original script passed
        # the resulting None on to `checkPermission` and raised there.
        attachment = self.create_attachment()
        self.assertIsNone(attachment.getPrimaryField())
        self.assertRaises(NotFound, self.get_view(attachment))


def test_suite():
    from unittest import makeSuite
    from unittest import TestSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestATDownload))
    return suite
