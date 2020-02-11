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

ACTIONS_TO_INDEXES = {
    "Analysis": {
        "assign": [
            "getAnalyst",
            "getWorksheetUID",
        ],
        "cancel": [
            "is_active",
        ],
        "reinstate": [
            "is_active",
        ],
        "reject": [
            "getWorksheetUID",
        ],
        "retract": [
            "id",
            "title",
        ],
        "submit": [
            "getAnalyst",
            "getDueDate",
            "getInstrumentUID",
            "getMethodUID",
            "getResultCaptureDate",
        ],
        "unassign": [
            "getAnalyst",
            "getWorksheetUID",
        ],
        "verify": [
            "review_state",
        ],
    },

    "DuplicateAnalysis": {
        "retract": [
            "id",
            "title",
        ],
        "submit": [
            "getAnalyst",
            "getDueDate",
            "getInstrumentUID",
            "getMethodUID",
            "getResultCaptureDate",
        ],
        "unassign": None,
        "verify": [
            "review_state",
        ],
    },

    "ReferenceAnalysis": {
        "retract": [
            "review_state",
        ],
        "submit": [
            "getAnalyst",
            "getDueDate",
            "getInstrumentUID",
            "getMethodUID",
            "getResultCaptureDate",
            "review_state",
        ],
        "unassign": None,
        "verify": [
            "review_state",
        ],
    },

    "Worksheet": {
        "attach": [
            "getAnalysesUIDs",
        ],
        "rollback_to_open": [
            "getAnalysesUIDs",
        ],
        "submit": [
            "getAnalysesUIDs",
        ],
        "verify": [
            "getAnalysesUIDs",
        ],
    },

    "AnalysisRequest": {
        "receive": {
            "getDueDate",
            "getDateReceived",
            "is_received",
        },
        "rollback_to_receive": [
            "assigned_state",
            "getDueDate",
        ],
        "submit": [
            "assigned_state",
            "getDueDate",
        ],
        "verify": [
            "getDateVerified",
        ],
        "cancel": [
            "is_active",
        ],
        "reinstate": [
            "is_active",
        ],
    }
}
