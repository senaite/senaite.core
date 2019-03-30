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

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.controlpanel.bika_analysisspecs import AnalysisSpecsView
from bika.lims.permissions import AddAnalysisSpec


class ClientAnalysisSpecsView(AnalysisSpecsView):

    def __init__(self, context, request):
        super(ClientAnalysisSpecsView, self).__init__(context, request)
        self.contentFilter["getClientUID"] = api.get_uid(context)

    def before_render(self):
        """Before template render hook
        """
        # We want to display the nav tabs, so we do NOT want disable_border in
        # the request. Thus, do not call super.before_render

        mtool = api.get_tool("portal_membership")
        if not mtool.checkPermission(AddAnalysisSpec, self.context):
            del self.context_actions[_("Add")]
