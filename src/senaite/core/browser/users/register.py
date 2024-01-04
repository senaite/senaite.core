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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from plone.app.users.browser.register import AddUserForm as BaseAddUserForm
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AddUserForm(BaseAddUserForm):
    template = ViewPageTemplateFile("templates/newuser_form.pt")

    def updateFields(self):
        super(AddUserForm, self).updateFields()

        # remove groups field from registration
        if "groups" in self.fields:
            del self.fields["groups"]

    def updateWidgets(self):
        super(AddUserForm, self).updateWidgets()

    def updateActions(self):
        super(AddUserForm, self).updateActions()
        self.actions["register"].klass = "btn btn-sm btn-success"
