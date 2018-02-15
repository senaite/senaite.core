# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
