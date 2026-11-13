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
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from senaite.core.adapters.localroles import DynamicLocalRoleAdapter
from senaite.core.interfaces import IDynamicLocalRoles
from senaite.core.tests.base import DataTestCase
from zope.component import getGlobalSiteManager
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.interface import implementer

GROUP_ID = "Analysts"
DYNAMIC_ROLE = "ClientGuest"


class IDynamicRolesMarker(Interface):
    """Marks the content the dynamic roles of the test apply to
    """


@implementer(IDynamicLocalRoles)
class DynamicRolesStub(object):
    """Gives the test user a dynamic local role
    """

    def __init__(self, context):
        self.context = context

    def getRoles(self, principal_id):
        if principal_id == TEST_USER_ID:
            return [DYNAMIC_ROLE]
        return []


class TestDynamicLocalRoles(DataTestCase):
    """The local roles of a context, with and without dynamic local roles
    """

    def setUp(self):
        super(TestDynamicLocalRoles, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def create_client(self, client_id):
        client = api.create(self.portal.clients, "Client",
                            Name=client_id, ClientID=client_id)
        client.manage_setLocalRoles(TEST_USER_ID, ["Owner"])
        client.manage_setLocalRoles(GROUP_ID, ["Reader"])
        return client

    def get_roles_by_member(self, adapter):
        """The roles of the context, asked for member by member
        """
        roles = {}
        for principal_id in adapter.getMemberIds():
            member_roles = adapter.getRoles(principal_id)
            if member_roles:
                roles[principal_id] = sorted(member_roles)
        return roles

    def get_all_roles(self, adapter):
        return {principal_id: sorted(roles)
                for principal_id, roles in adapter.getAllRoles()}

    def test_roles_without_dynamic_roles(self):
        client = self.create_client("C1")
        adapter = DynamicLocalRoleAdapter(client)
        self.assertFalse(adapter.hasDynamicRoles())

        roles = self.get_all_roles(adapter)
        self.assertEqual(roles, self.get_roles_by_member(adapter))
        self.assertEqual(roles[TEST_USER_ID], ["Owner"])
        # a group is no member, its local roles are not listed here
        self.assertNotIn(GROUP_ID, roles)

    def test_roles_with_dynamic_roles(self):
        client = self.create_client("C2")
        alsoProvides(client, IDynamicRolesMarker)
        sm = getGlobalSiteManager()
        sm.registerAdapter(DynamicRolesStub, (IDynamicRolesMarker,),
                           IDynamicLocalRoles, name="test")
        self.addCleanup(sm.unregisterAdapter, DynamicRolesStub,
                        (IDynamicRolesMarker,), IDynamicLocalRoles,
                        name="test")

        adapter = DynamicLocalRoleAdapter(client)
        self.assertTrue(adapter.hasDynamicRoles())

        roles = self.get_all_roles(adapter)
        self.assertEqual(roles, self.get_roles_by_member(adapter))
        self.assertEqual(roles[TEST_USER_ID], [DYNAMIC_ROLE, "Owner"])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDynamicLocalRoles))
    return suite
