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
# Copyright 2018-2019 by it's authors.
# Some rights reserved, see README and LICENSE.

from plone.app.contentmenu.menu import WorkflowMenu as BaseClass


class WorkflowMenu(BaseClass):

    def getMenuItems(self, context, request):
        """Overrides the workflow actions menu displayed top right in the
        object's view. Displays the current state of the object, as well as a
        list with the actions that can be performed.
        The option "Advanced.." is not displayed and the list is populated with
        all allowed transitions for the object.
        """
        actions = super(WorkflowMenu, self).getMenuItems(context, request)
        # Remove status history menu item ('Advanced...')
        actions = [action for action in actions
            if not action['action'].endswith('/content_status_history')]
        return actions
