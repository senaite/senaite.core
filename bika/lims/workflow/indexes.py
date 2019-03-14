# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

# Mapping of indexes to be reindexed for each portal type after a given
# transition is performed.
# - If None is set for a given portal type and transition, doActionFor will
#   only reindex "review_state"
# - If a given transition is not present or contains an empty list, doActionFor
#   will reindex all indexes.
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
