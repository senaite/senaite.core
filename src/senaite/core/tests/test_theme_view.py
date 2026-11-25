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

from senaite.core.browser.globals.theme import SenaiteTheme
from senaite.core.tests.base import BaseTestCase
from zExceptions import NotFound
from zope.traversing.interfaces import TraversalError

ICON = "sample"


class ThemeViewTestCase(BaseTestCase):
    """The theme view only gives access to its icon functions
    """

    def get_view(self, *subpath, **form):
        self.request.form.clear()
        self.request.form.update(form)
        view = SenaiteTheme(self.portal, self.request)
        for name in subpath:
            view.publishTraverse(self.request, name)
        return view

    def get_icon_url(self):
        portal_url = self.portal.absolute_url()
        return "{}/{}".format(portal_url, self.get_view().icon_path(ICON))

    def test_an_icon_url_is_returned_by_url(self):
        view = self.get_view("icon_url", ICON)
        self.assertEqual(view(), self.get_icon_url())

    def test_an_icon_tag_is_returned_by_url(self):
        view = self.get_view("icon_tag", ICON, width="16")
        self.assertIn('width="16"', view())

    def test_the_view_without_a_subpath_is_not_found(self):
        view = self.get_view()
        self.assertRaises(NotFound, view)

    def test_an_unknown_function_is_not_found(self):
        view = self.get_view("unknown", ICON)
        self.assertRaises(NotFound, view)

    def test_a_private_method_is_not_found(self):
        view = self.get_view("_get_last_modified", ICON)
        self.assertRaises(NotFound, view)

    def test_the_context_is_not_found(self):
        view = self.get_view("context")
        self.assertRaises(NotFound, view)

    def test_the_icon_mapping_is_not_found_by_url(self):
        view = self.get_view("icons", ICON)
        self.assertRaises(NotFound, view)

    def test_an_icon_function_without_a_name_is_not_found(self):
        view = self.get_view("icon_url")
        self.assertRaises(NotFound, view)

    def test_an_icon_function_with_more_segments_is_not_found(self):
        view = self.get_view("icon_url", ICON, "more")
        self.assertRaises(NotFound, view)

    def test_an_icon_url_is_traversed_in_templates(self):
        traverser = self.get_view().traverse("icon_url", [ICON])
        self.assertEqual(traverser.traverse(ICON, []), self.get_icon_url())

    def test_the_icon_mapping_is_traversed_in_templates(self):
        icons = self.get_view().traverse("icons", [])
        self.assertIn(ICON, icons())

    def test_other_names_are_not_traversed_in_templates(self):
        view = self.get_view()
        self.assertRaises(TraversalError, view.traverse, "portal", [])
        self.assertRaises(TraversalError, view.traverse, "context", [])
