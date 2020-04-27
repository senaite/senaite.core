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

from AccessControl import getSecurityManager
from bika.lims.api import get_portal
from bika.lims.api import get_tool
from Products.CMFPlone.RegistrationTool import get_member_by_login_name
from Products.PlonePAS.tools.groupdata import GroupData
from Products.PlonePAS.tools.memberdata import MemberData


def get_user(user=None):
    """Get the user object

    :param user: A user id, memberdata object or None for the current user
    :returns: Plone User (PlonePAS) / Propertied User (PluggableAuthService)
    """
    if user is None:
        # Return the current authenticated user
        user = getSecurityManager().getUser()
    elif isinstance(user, MemberData):
        # MemberData wrapped user -> get the user object
        user = user.getUser()
    elif isinstance(user, basestring):
        # User ID -> get the user
        user = get_member_by_login_name(get_portal(), user, False)
        if user:
            user = user.getUser()
    return user


def get_user_id(user=None):
    """Get the user id of the current authenticated user

    :param user: A user id, memberdata object or None for the current user
    :returns: Plone user ID
    """
    user = get_user(user)
    if user is None:
        return None
    return user.getId()


def get_group(group):
    """Return the group

    :param group: The group name/id
    :returns: Group
    """
    portal_groups = get_tool("portal_groups")
    if isinstance(group, basestring):
        group = portal_groups.getGroupById(group)
    elif isinstance(group, GroupData):
        group = group
    return group


def get_groups(user=None):
    """Return the groups of the user

    :param user: A user id, memberdata object or None for the current user
    :returns: List of groups
    """
    portal_groups = get_tool("portal_groups")
    user = get_user(user)
    if user is None:
        return []
    return portal_groups.getGroupsForPrincipal(user)


def add_group(group, user=None):
    """Add the user to the group
    """
    user = get_user(user)

    if user is None:
        raise ValueError("User '{}' not found".format(repr(user)))

    if isinstance(group, basestring):
        group = [group]
    elif isinstance(group, GroupData):
        group = [group]

    portal_groups = get_tool("portal_groups")
    for group in map(get_group, group):
        if group is None:
            continue
        portal_groups.addPrincipalToGroup(get_user_id(user), group.getId())

    return get_groups(user)


def del_group(group, user=None):
    """Remove the user to the group
    """
    user = get_user(user)

    if user is None:
        raise ValueError("User '{}' not found".format(repr(user)))

    if isinstance(group, basestring):
        group = [group]
    elif isinstance(group, GroupData):
        group = [group]

    portal_groups = get_tool("portal_groups")
    for group in map(get_group, group):
        if group is None:
            continue
        portal_groups.removePrincipalFromGroup(
            get_user_id(user), group.getId())

    return get_groups(user)
