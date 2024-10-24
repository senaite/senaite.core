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

from bika.lims import api


def _reindexWorkflowVariables(self, ob):
    """This function is called by DCWorkflow immediately after the workflow
    action is invoked in WorkflowTool.doActionFor.

    The original function is only responsible of reindexing the variables that
    may have changed due to the transition (e.g review_state) along with
    security-related indexes. However, the original function does two calls
    to reindexObject, one for workflow variables and another one for the
    security-related indexes. Metadata is updated on both calls as well, cause
    those workflow-variables might also be stored as metadata.

    Since quite often the transition involves changes not only in
    workflow-related variables, but to other field values, it becomes almost
    a requirement to always reindex the object after a transition. Therefore,
    we simply do a full reindexObject here instead of taking only some indexes
    into account.
    """
    if api.is_temporary(ob):
        return

    # do a full reindex
    ob.reindexObject()
