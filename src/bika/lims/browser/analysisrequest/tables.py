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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analyses.qc import QCAnalysesView
from bika.lims.browser.analyses.view import AnalysesView


class LabAnalysesTable(AnalysesView):
    """Lab Analyses Listing Table for ARs
    """

    def __init__(self, context, request):
        super(LabAnalysesTable, self).__init__(context, request)

        self.contentFilter.update({
            "getPointOfCapture": "lab",
            "getAncestorsUIDs": [api.get_uid(context)]
        })

        self.form_id = "lab_analyses"
        self.allow_edit = True
        self.show_workflow_action_buttons = True
        self.show_select_column = True
        self.show_search = False


class FieldAnalysesTable(AnalysesView):
    """Field Analyses Listing Table for ARs
    """

    def __init__(self, context, request):
        super(FieldAnalysesTable, self).__init__(context, request)

        self.contentFilter.update({
            "getPointOfCapture": "field",
            "getAncestorsUIDs": [api.get_uid(context)]
        })

        self.form_id = "field_analyses"
        self.allow_edit = True
        self.show_workflow_action_buttons = True
        self.show_select_column = True
        self.show_search = False


class QCAnalysesTable(QCAnalysesView):
    """QC Analyses Listing Table for ARs
    """

    def __init__(self, context, request):
        super(QCAnalysesTable, self).__init__(context, request)

        self.form_id = "qc_analyses"
        self.allow_edit = False
        self.show_select_column = False
        self.show_workflow_action_buttons = False
        self.show_search = False
