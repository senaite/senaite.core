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
from zExceptions import NotFound

# Ignore default Plone roles
IGNORE_ROLES = [
    "Reader",
    "Editor",
    "Contributor",
    "Reviewer",
]


class SharingView(BaseView):
    """Custom Sharing View for lab-side content.
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
    """Disable @@sharing on Client / IClientAwareMixin content.

    Access is granted dynamically by
    ``senaite.core.security.clientrole``; persistent local-role
    grants here would defeat the purpose.
    """
    def __call__(self):
        raise NotFound("sharing")
