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

import six
from Acquisition import aq_inner
from bika.lims import api
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.controlpanel.browser.usergroups_usersoverview import \
    UsersOverviewControlPanel as BaseView
from senaite.core import logger
from senaite.core.catalog import CLIENT_CATALOG
from senaite.core.config.roles import HIDDEN_ROLES
from zExceptions import Forbidden


class UsersOverviewControlPanel(BaseView):
    """Custom userprefs controlpanel
    """

    @property
    def portal_roles(self):
        """Return only SENAITE Roles
        """
        pmemb = getToolByName(aq_inner(self.context), "portal_membership")
        roles = pmemb.getPortalRoles()
        return filter(lambda r: r not in HIDDEN_ROLES, roles)

    def get_clients(self):
        """Return all clients from the site
        """
        query = {"portal_type": "Client"}
        clients = api.search(query, CLIENT_CATALOG)
        return list(map(api.get_object, clients))

    def clear_user_groups(self, user):
        """Clear all assigned groups of the user
        """
        groups = user.getGroups()
        pgm = api.get_tool("portal_groups")
        user_id = user.getId()
        for group in groups:
            try:
                pgm.removePrincipalFromGroup(user_id, group)
                logger.info("Clearing group '%s' for user '%s'" % (
                    group, user_id))
            except KeyError:
                # happens e.g. for `AuthenticatedUsers`
                logger.warn("Could not clear group '%s' for user '%s'" % (
                    group, user_id))
                continue

    def clear_user_roles(self, user):
        """Clear all assigned roles of the user
        """
        roles = user.getRoles()
        acl = api.get_tool("acl_users")
        prm = acl.portal_role_manager
        user_id = user.getId()
        for role in roles:
            try:
                prm.removeRoleFromPrincipal(role, user_id)
                logger.info("Clearing role '%s' for user '%s'" % (
                    role, user_id))
            except KeyError:
                # happens e.g. for `AuthenticatedUsers`
                logger.warn("Could not clear role '%s' for user '%s'" % (
                    role, user_id))
                continue

    def deleteMembers(self, member_ids):
        # this method exists to bypass the 'Manage Users' permission check
        # in the CMF member tool's version
        context = aq_inner(self.context)
        mtool = api.get_tool("portal_membership")

        # Delete members in acl_users.
        acl_users = context.acl_users
        if isinstance(member_ids, six.string_types):
            member_ids = (member_ids,)
        member_ids = list(member_ids)
        for member_id in member_ids[:]:
            member = mtool.getMemberById(member_id)
            if member is None:
                member_ids.remove(member_id)
            else:
                if not member.canDelete():
                    raise Forbidden
                if "Manager" in member.getRoles() and not self.is_zope_manager:
                    raise Forbidden
                # clear all role/group assignments
                self.clear_user_groups(member)
                self.clear_user_roles(member)

        try:
            acl_users.userFolderDelUsers(member_ids)
        except (AttributeError, NotImplementedError):
            raise NotImplementedError('The underlying User Folder '
                                      'doesn\'t support deleting members.')

        # Delete member data in portal_memberdata.
        mdtool = api.get_tool("portal_memberdata")
        if mdtool is not None:
            for member_id in member_ids:
                mdtool.deleteMemberData(member_id)

        # NOTE: the original call below iterates over **all** objects
        # recursively to remove the local roles, which takes ages!
        # The only place we allow local roles to be assigned are clients.
        # Therefore, we want to make sure to remove them just from there
        #
        # Delete members' local roles.
        # mtool.deleteLocalRoles(
        #     getUtility(ISiteRoot),
        #     member_ids,
        #     reindex=1,
        #     recursive=1
        # )
        #
        # XXX: Maybe we could index local role assignments in the future?
        for client in self.get_clients():
            mtool.deleteLocalRoles(client, member_ids, reindex=0, recursive=0)
<<<<<<< Updated upstream
=======

    def manageUser(self, users=[], resetpassword=[], delete=[]):
        """接管保存逻辑，忽略物理删除，仅维护禁用状态
        """
        # 中文注释：基类 __call__ 会把表单中所有 users.*:records 字段解析成
        # request.form['users'] 下的 record 对象列表（Zope 的 records 类型会
        # 剥掉 :records 后缀并按点号分组，users.disabled:records 会作为
        # disabled 属性挂到同一条 users.id:records 记录上）。因此不能再用
        # form.get("users.disabled:records") 这种带后缀的键读取（真实请求中
        # 永远取不到），直接遍历基类传入的 users 参数，取记录的 id / disabled
        # 属性即可。
        for user in (users or []):
            user_id = getattr(user, "id", None)
            if not user_id:
                continue
            set_account_disabled(user_id, bool(getattr(user, "disabled", None)))

        # 即使有人手工伪造 delete:list 提交，也不再执行物理删除。
        return super(UsersOverviewControlPanel, self).manageUser(
            users, resetpassword, [])
>>>>>>> Stashed changes
