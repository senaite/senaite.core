# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

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
