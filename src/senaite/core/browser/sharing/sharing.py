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

from plone.app.workflow.browser.sharing import SharingView as BaseView
from plone.memoize.instance import memoize
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# Ignore default Plone roles
IGNORE_ROLES = [
    "Reader",
    "Editor",
    "Contributor",
    "Reviewer",
]


class SharingView(BaseView):
    """Custom Sharing View for lab-side content.

    Client-tree content (Client / IClientAwareMixin) gets a different,
    explanatory view (see ``ClientTreeSharingDisabledView``) because
    sharing is granted there via the dynamic role provider when a
    contact is linked to a user, not via persistent local roles.
    """
    STICKY = ()
    template = ViewPageTemplateFile("templates/client_sharing.pt")

    @memoize
    def roles(self):
        pairs = super(SharingView, self).roles()
        return filter(lambda pair: pair.get("id") not in IGNORE_ROLES, pairs)

    def can_edit_inherit(self):
        return False


class ClientTreeSharingDisabledView(BrowserView):
    """Replacement for @@sharing on Client / IClientAwareMixin content.

    Sharing is disabled on the client tree because access is granted
    dynamically by ``senaite.core.security.clientrole`` based on the
    ``linked_client_uid`` member property set when a contact is linked
    to a user. Using the @@sharing tab to grant local roles here would
    write persistent ``__ac_local_roles__`` entries and trigger a
    recursive ``reindexObjectSecurity`` over the client tree — the
    exact cost the dynamic-role refactor was introduced to eliminate.
    """
    template = ViewPageTemplateFile(
        "templates/client_sharing_disabled.pt")

    def __call__(self):
        return self.template()
