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

import json

from AccessControl import Unauthorized
from bika.lims import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from senaite.core.browser.form.ajax import FormView
from senaite.core.tests.base import BaseTestCase

DATA_IMPORT = "data_import_form"
ADD_SAMPLE_TYPE = "++add++SampleType"


class AjaxFormTestCase(BaseTestCase):
    """The ajax form checks who may use a form before it calls its adapter
    """

    def as_roles(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        login(self.portal, TEST_USER_NAME)

    def get_view(self, context, adapter_name, **form):
        self.request.form.clear()
        self.request.form.update(form, form_adapter_name=adapter_name)
        self.request.set("BODY", "")
        return FormView(context, self.request)

    def sampletypes(self):
        return api.get_senaite_setup().get("sampletypes")

    def test_anonymous_cannot_use_the_data_import_form(self):
        logout()
        view = self.get_view(self.portal, DATA_IMPORT)
        self.assertRaises(Unauthorized, view.initialized)
        self.assertRaises(Unauthorized, view.submit)

    def test_anonymous_cannot_import_setup_data(self):
        logout()
        view = self.get_view(self.portal, DATA_IMPORT, setupexisting="1",
                             existing="bika.lims:test")
        self.assertRaises(Unauthorized, view.submit)

    def test_client_cannot_use_an_add_form(self):
        self.as_roles("Client")
        view = self.get_view(self.sampletypes(), ADD_SAMPLE_TYPE)
        self.assertRaises(Unauthorized, view.initialized)

    def test_client_cannot_use_an_edit_form(self):
        self.as_roles("Client")
        view = self.get_view(api.get_senaite_setup(), None)
        self.assertRaises(Unauthorized, view.initialized)

    def test_an_unknown_add_form_is_refused(self):
        self.as_roles("LabManager")
        view = self.get_view(self.sampletypes(), "++add++NoSuchType")
        self.assertEqual(json.loads(view.initialized()), {})

    def test_analyst_cannot_import_setup_data(self):
        self.as_roles("Analyst")
        view = self.get_view(self.portal, DATA_IMPORT, setupexisting="1",
                             existing="bika.lims:test")
        self.assertRaises(Unauthorized, view.submit)

    def test_lab_manager_uses_the_forms(self):
        self.as_roles("LabManager")
        view = self.get_view(self.portal, DATA_IMPORT)
        answer = json.loads(view.initialized())
        self.assertEqual(answer["hide"], [{"name": "exim"}])
        view = self.get_view(self.sampletypes(), ADD_SAMPLE_TYPE)
        self.assertIsInstance(json.loads(view.initialized()), dict)
