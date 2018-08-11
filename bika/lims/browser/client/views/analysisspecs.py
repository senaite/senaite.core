# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.controlpanel.bika_analysisspecs import BaseAnalysisSpecsView
from bika.lims.permissions import AddAnalysisSpec


class ClientAnalysisSpecsView(BaseAnalysisSpecsView):

    def __init__(self, context, request):
        super(ClientAnalysisSpecsView, self).__init__(context, request)
        self.contentFilter["getClientUID"] = api.get_uid(context)

    def before_render(self):
        """Before template render hook
        """
        mtool = api.get_tool("portal_membership")
        if mtool.checkPermission(AddAnalysisSpec, self.context):
            del self.context_actions[_("Add")]
