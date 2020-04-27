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
from AccessControl.Permission import Permission
from bika.lims import api
from bika.lims.api.user import get_user
from bika.lims.api.user import get_user_id


def get_security_manager():
    """Get a security manager for the current thread

    See `AccessControl.SecurityManagement.getSecurityManager`

    :returns: Security manager for the current thread
    """
    return getSecurityManager()


def get_possible_permissions_for(brain_or_object):
    """Get the possible permissions for given the object

    See `IRoleManager.possible_permissions`

    :param brain_or_object: Catalog brain or object
    :returns: List of permissions
    """
    obj = api.get_object(brain_or_object)
    return obj.possible_permissions()


def get_mapped_permissions_for(brain_or_object):
    """Get the mapped permissions for the given object

    A mapped permission is one that is used in the object.

    Each permission string, e.g. "senaite.core: Field: Edit Analysis Remarks" is
    translated by the function `AccessControl.Permission.pname` to a valid
    attribute name:

    >>> from bika.lims.permissions import FieldEditAnalysisResult
    >>> AccessControl.Permission import pname
    >>> pname(FieldEditAnalysisResult)
    _Field__Edit_Result_Permission

    This attribute is looked up in the object by `getPermissionMapping`:

    >>> from AccessControl.PermissionMapping import getPermissionMapping
    >>> getPermissionMapping(FieldEditAnalysisResult, wrapper)
    ("Manager", "Sampler")

    Therefore, only those permissions which have roles mapped on the object
    or by objects within the acquisition chain are considered.

    Code extracted from `IRoleManager.manage_getUserRolesAndPermissions`

    :param brain_or_object: Catalog brain or object
    :returns: List of permissions
    """
    obj = api.get_object(brain_or_object)
    mapping = obj.manage_getPermissionMapping()
    return map(lambda item: item["permission_name"], mapping)


def get_allowed_permissions_for(brain_or_object, user=None):
    """Get the allowed permissions for the given object

    Code extracted from `IRoleManager.manage_getUserRolesAndPermissions`

    :param brain_or_object: Catalog brain or object
    :param user: A user ID, user object or None (for the current user)
    :returns: List of allowed permissions
    """
    allowed = []
    user = get_user(user)
    obj = api.get_object(brain_or_object)
    for permission in get_mapped_permissions_for(brain_or_object):
        if user.has_permission(permission, obj):
            allowed.append(permission)
    return allowed


def get_disallowed_permissions_for(brain_or_object, user=None):
    """Get the disallowed permissions for the given object

    Code extracted from `IRoleManager.manage_getUserRolesAndPermissions`

    :brain_or_object: Catalog brain or object
    :param user: A user ID, user object or None (for the current user)
    :returns: List of disallowed permissions
    """
    disallowed = []
    user = get_user(user)
    obj = api.get_object(brain_or_object)
    for permission in get_mapped_permissions_for(brain_or_object):
        if not user.has_permission(permission, obj):
            disallowed.append(permission)
    return disallowed


def check_permission(permission, brain_or_object):
    """Check whether the security context allows the given permission on
       the given brain or object.

    N.B.: This includes also acquired permissions

    :param permission: Permission name
    :brain_or_object: Catalog brain or object
    :returns: True if the permission is granted
    """
    sm = get_security_manager()
    obj = api.get_object(brain_or_object)
    return sm.checkPermission(permission, obj) == 1


def get_permissions_for_role(role, brain_or_object):
    """Return the permissions of the role which are granted on the object

    Code extracted from `IRoleManager.permissionsOfRole`

    :param role: The role to check the permission
    :param brain_or_object: Catalog brain or object
    :returns: List of permissions of the role
    """
    obj = api.get_object(brain_or_object)

    # Raise an error if the role is invalid
    valid_roles = get_valid_roles_for(obj)
    if role not in valid_roles:
        raise ValueError("The Role '{}' is invalid.".format(role))

    out = []
    for item in obj.ac_inherited_permissions(1):
        name, value = item[:2]
        # Permission maps a named permission to a set of attribute names
        permission = Permission(name, value, obj)
        if role in permission.getRoles():
            out.append(name)
    return out


def get_roles_for_permission(permission, brain_or_object):
    """Return the roles of the permission that is granted on the object

    Code extracted from `IRoleManager.rolesOfPermission`

    :param permission: The permission to get the roles
    :param brain_or_object: Catalog brain or object
    :returns: List of roles having the permission
    """
    obj = api.get_object(brain_or_object)
    valid_roles = get_valid_roles_for(obj)
    for item in obj.ac_inherited_permissions(1):
        name, value = item[:2]
        # found the requested permission
        if name == permission:
            # Permission maps a named permission to a set of attribute names
            permission = Permission(name, value, obj)
            roles = permission.getRoles()
            # return only valid roles that have the permission granted
            return filter(lambda r: r in valid_roles, roles)
    # Raise an error if the permission is invalid
    raise ValueError("The permission {} is invalid.".format(permission))


def get_roles(user=None):
    """Get the global defined roles of the user

    Code extracted from `IRoleManager.manage_getUserRolesAndPermissions`

    :param user: A user ID, user object or None (for the current user)
    :returns: List of global granted roles
    """
    user = get_user(user)
    return sorted(user.getRoles())


def get_local_roles_for(brain_or_object, user=None):
    """Get the local defined roles on the context

    Code extracted from `IRoleManager.get_local_roles_for_userid`

    :param brain_or_object: Catalog brain or object
    :param user: A user ID, user object or None (for the current user)
    :returns: List of granted local roles on the given object
    """
    user_id = get_user_id(user)
    obj = api.get_object(brain_or_object)
    return sorted(obj.get_local_roles_for_userid(user_id))


def grant_local_roles_for(brain_or_object, roles, user=None):
    """Grant local roles for the object

    Code extracted from `IRoleManager.manage_addLocalRoles`

    :param brain_or_object: Catalog brain or object
    :param user: A user ID, user object or None (for the current user)
    :param roles: The local roles to grant for the current user
    """
    user_id = get_user_id(user)
    obj = api.get_object(brain_or_object)

    if isinstance(roles, basestring):
        roles = [roles]

    obj.manage_addLocalRoles(user_id, roles)
    return get_local_roles_for(brain_or_object)


def revoke_local_roles_for(brain_or_object, roles, user=None):
    """Revoke local roles for the object

    Code extracted from `IRoleManager.manage_setLocalRoles`

    :param brain_or_object: Catalog brain or object
    :param roles: The local roles to revoke for the current user
    :param user: A user ID, user object or None (for the current user)
    """
    user_id = get_user_id(user)
    obj = api.get_object(brain_or_object)
    valid_roles = get_valid_roles_for(obj)
    to_grant = list(get_local_roles_for(obj))

    if isinstance(roles, basestring):
        roles = [roles]

    for role in roles:
        if role in to_grant:
            if role not in valid_roles:
                raise ValueError("The Role '{}' is invalid.".format(role))
            # Remove the role
            to_grant.remove(role)

    if len(to_grant) > 0:
        obj.manage_setLocalRoles(user_id, to_grant)
    else:
        obj.manage_delLocalRoles([user_id])
    return get_local_roles_for(brain_or_object)


def get_valid_roles_for(brain_or_object):
    """Get valid roles from the acquisition chain

    Code extracted from `IRoleManager`

    Traverses up the acquisition chain (`obj.__parent__`) and gathers all
    `obj.__ac__roles__` tuples

    :brain_or_object: Catalog brain or object
    :returns: List of valid roles
    """
    obj = api.get_object(brain_or_object)
    return sorted(obj.valid_roles())


def grant_permission_for(brain_or_object, permission, roles, acquire=0):
    """Grant the permission for the object to the defined roles

    Code extracted from `IRoleManager.manage_permission`

    :param brain_or_object: Catalog brain or object
    :param permission: The permission to be granted
    :param roles: The roles the permission to be granted to
    :param acquire: Flag to acquire the permission
    """
    obj = api.get_object(brain_or_object)
    valid_roles = get_valid_roles_for(obj)
    to_grant = list(get_roles_for_permission(permission, obj))

    if isinstance(roles, basestring):
        roles = [roles]

    for role in roles:
        if role not in to_grant:
            if role not in valid_roles:
                raise ValueError("The Role '{}' is invalid.".format(role))
            # Append the role
            to_grant.append(role)

    manage_permission_for(obj, permission, to_grant, acquire=acquire)


def revoke_permission_for(brain_or_object, permission, roles, acquire=0):
    """Revoke the permission for the object to the defined roles

    Code extracted from `IRoleManager.manage_permission`

    :param brain_or_object: Catalog brain or object
    :param permission: The permission to be granted
    :param roles: The roles the permission to be granted to
    :param acquire: Flag to acquire the permission
    """
    obj = api.get_object(brain_or_object)
    valid_roles = get_valid_roles_for(obj)
    to_grant = list(get_roles_for_permission(permission, obj))

    if isinstance(roles, basestring):
        roles = [roles]

    for role in roles:
        if role in to_grant:
            if role not in valid_roles:
                raise ValueError("The Role '{}' is invalid.".format(role))
            # Remove the role
            to_grant.remove(role)

    manage_permission_for(obj, permission, to_grant, acquire=acquire)


def manage_permission_for(brain_or_object, permission, roles, acquire=0):
    """Change the settings for the given permission.

    Code extracted from `IRoleManager.manage_permission`

    :param brain_or_object: Catalog brain or object
    :param permission: The permission to be granted
    :param roles: The roles the permission to be granted to
    :param acquire: Flag to acquire the permission
    """
    obj = api.get_object(brain_or_object)

    if isinstance(roles, basestring):
        roles = [roles]

    for item in obj.ac_inherited_permissions(1):
        name, value = item[:2]
        if name == permission:
            permission = Permission(name, value, obj)
            if acquire:
                roles = list(roles)
            else:
                roles = tuple(roles)
            permission.setRoles(roles)
            return

    # Raise an error if the permission is invalid
    raise ValueError("The permission {} is invalid.".format(permission))
