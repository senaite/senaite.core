# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims.browser.analyses.view import AnalysesView
from bika.lims import bikaMessageFactory as _


class BaseAnalysesTable(AnalysesView):
    """Base Analyses Table
    """
    def __init__(self, context, request):
        super(BaseAnalysesTable, self).__init__(context, request)
        self.contentFilter.update({
            "getRequestUID": api.get_uid(context)
        })

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

    def contents_table(self):
        self.update()
        self.before_render()
        return self.ajax_contents_table()


class LabAnalysesTable(BaseAnalysesTable):
    """Lab Analyses Listing Table for ARs
    """

    def __init__(self, context, request):
        super(LabAnalysesTable, self).__init__(context, request)
        self.contentFilter.update({
            "getPointOfCapture": "lab",
        })
        self.form_id = "lab_analyses"


class FieldAnalysesTable(BaseAnalysesTable):
    """Field Analyses Listing Table for ARs
    """

    def __init__(self, context, request):
        super(FieldAnalysesTable, self).__init__(context, request)
        self.contentFilter.update({
            "getPointOfCapture": "field",
        })
        self.form_id = "field_analyses"


class QCAnalysesTable(BaseAnalysesTable):
    """QC Analyses Listing Table for ARs
    """

    def __init__(self, context, request):
        super(QCAnalysesTable, self).__init__(context, request)

        self.contentFilter.update({
        })

        self.form_id = "qc_analyses"
        self.allow_edit = False
        self.show_select_column = False
        self.show_workflow_action_buttons = False
