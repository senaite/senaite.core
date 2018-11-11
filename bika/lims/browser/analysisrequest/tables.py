# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.analyses.qc import QCAnalysesView
from bika.lims.browser.analyses.view import AnalysesView


class BaseAnalysesTable(AnalysesView):
    """Base Analyses Table
    """
    def __init__(self, context, request):
        super(BaseAnalysesTable, self).__init__(context, request)

        self.allow_edit = True
        self.show_workflow_action_buttons = True
        self.show_select_column = True

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "transitions": [
                    {"id": "submit"},
                    {"id": "retract"},
                    {"id": "verify"},
                ],
                "columns": self.columns.keys()
             },
        ]


class LabAnalysesTable(BaseAnalysesTable):
    """Lab Analyses Listing Table for ARs
    """

    def __init__(self, context, request):
        super(LabAnalysesTable, self).__init__(context, request)
        self.contentFilter.update({
            "getPointOfCapture": "lab",
            "getRequestUID": api.get_uid(context)
        })
        self.form_id = "lab_analyses"


class FieldAnalysesTable(BaseAnalysesTable):
    """Field Analyses Listing Table for ARs
    """

    def __init__(self, context, request):
        super(FieldAnalysesTable, self).__init__(context, request)
        self.contentFilter.update({
            "getPointOfCapture": "field",
            "getRequestUID": api.get_uid(context)
        })
        self.form_id = "field_analyses"


class QCAnalysesTable(QCAnalysesView):
    """QC Analyses Listing Table for ARs
    """

    def __init__(self, context, request):
        super(QCAnalysesTable, self).__init__(context, request)

        self.form_id = "qc_analyses"
        self.allow_edit = False
        self.show_select_column = False
        self.show_workflow_action_buttons = False
