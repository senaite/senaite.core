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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.utils import getToolByName
from bika.lims import api
from bika.lims import workflow as wf
from bika.lims.api import analysis as api_analysis
from bika.lims.utils import changeWorkflowState
from bika.lims.utils import tmpID
from bika.lims.utils.analysis import create_reference_analysis
from bika.lims.workflow import skip
from senaite.core.workflow import ANALYSIS_WORKFLOW
from senaite.core.config.worksheet import WORKSHEETS_FOLDER_ID

IGNORE_FIELDS = [
    "UID",
    "id",
    "title",
    "allowDiscussion",
    "subject",
    "description",
    "location",
    "contributors",
    "creators",
    "effectiveDate",
    "expirationDate",
    "language",
    "rights",
    "creation_date",
    "modification_date",
    "layout_view",  # ws
    "analyses",  # ws
]


def copy_src_fields_to_dst(src, dst):
    # These will be ignored when copying field values between analyses

    fields = src.Schema().fields()
    for field in fields:
        fieldname = field.getName()
        if fieldname in IGNORE_FIELDS:
            continue
        getter = getattr(src, 'get' + fieldname,
                         src.Schema().getField(fieldname).getAccessor(src))
        setter = getattr(dst, 'set' + fieldname,
                         dst.Schema().getField(fieldname).getMutator(dst))
        if getter is None or setter is None:
            # ComputedField
            continue
        setter(getter())


def after_retract(worksheet):
    """Retracts all analyses the worksheet contains
    """
    for analysis in worksheet.getAnalyses():
       wf.doActionFor(analysis, "retract")


def after_remove(worksheet):
    """Removes the worksheet from the system
    """
    # bypass security checks on object removal. The removal of worksheet
    # objects is governed by "Transition: Remove Worksheet" permission at
    # worksheet level, along with a specific guard to ensure that only empty
    # worksheets can be removed. Therefore, better keep the "Delete objects"
    # permission at Worksheets folder level as false, because is less specific
    api.delete(worksheet, check_permissions=False)


def after_reject(worksheet):
    """Copy real analyses to RejectAnalysis, with link to real
    create a new worksheet, with the original analyses, and new
    duplicates and references to match the rejected
    worksheet.
    """
    if skip(worksheet, "reject"):
        return
    workflow = getToolByName(worksheet, "portal_workflow")
    analysis_positions = {}
    for item in worksheet.getLayoutView():
        analysis_positions[item["analysis_uid"]] = item["position"]
    old_layout = []
    new_layout = []

    # New worksheet
    portal = api.get_portal()
    kwargs = {
        "container": portal.get(WORKSHEETS_FOLDER_ID),
        "portal_type": "Worksheet",
        "skip": IGNORE_FIELDS,
    }
    new_ws = api.copy_object(worksheet, **kwargs)

    # Objects are being created inside other contexts, but we want their
    # workflow handlers to be aware of which worksheet this is occurring in.
    # We save the worksheet in request['context_uid'].
    # We reset it again below....  be very sure that this is set to the
    # UID of the containing worksheet before invoking any transitions on
    # analyses.
    worksheet.REQUEST["context_uid"] = new_ws.UID()

    # loop all analyses
    analyses = worksheet.getAnalyses()
    new_ws_analyses = []
    old_ws_analyses = []
    for analysis in analyses:
        # Skip published or verified analyses
        review_state = workflow.getInfoFor(analysis, "review_state", "")
        if review_state in ["published", "verified", "retracted"]:
            old_ws_analyses.append(analysis.UID())
            old_layout.append({
                "type": "a",
                "analysis_uid": analysis.UID(),
                "container_uid": analysis.aq_parent.UID()
            })
            continue
        # Normal analyses:
        # - Create matching RejectAnalysis inside old WS
        # - Link analysis to new WS in same position
        # - Copy all field values
        # - Clear analysis result, and set Retested flag
        if api_analysis.is_analysis(analysis):
            reject = _createObjectByType("RejectAnalysis", worksheet, tmpID())
            reject.unmarkCreationFlag()
            copy_src_fields_to_dst(analysis, reject)
            reject.setAnalysis(analysis)
            reject.reindexObject()
            analysis.edit(
                Result=None,
                Retested=True,
            )
            analysis.reindexObject()
            position = analysis_positions[analysis.UID()]
            old_ws_analyses.append(reject.UID())
            old_layout.append({
                "position": position,
                "type": "r",
                "analysis_uid": reject.UID(),
                "container_uid": worksheet.UID()
            })
            new_ws_analyses.append(analysis.UID())
            new_layout.append({
                "position": position,
                "type": "a",
                "analysis_uid": analysis.UID(),
                "container_uid": analysis.aq_parent.UID()
            })
        # Reference analyses
        # - Create a new reference analysis in the new worksheet
        # - Transition the original analysis to 'rejected' state
        if api_analysis.is_reference_analysis(analysis):
            service_uid = analysis.getServiceUID()
            reference = analysis.aq_parent
            new_reference = create_reference_analysis(reference, service_uid)
            reference_type = new_reference.getReferenceType()
            new_analysis_uid = api.get_uid(new_reference)
            position = analysis_positions[analysis.UID()]
            old_ws_analyses.append(analysis.UID())
            old_layout.append({
                "position": position,
                "type": reference_type,
                "analysis_uid": analysis.UID(),
                "container_uid": reference.UID()
            })
            new_ws_analyses.append(new_analysis_uid)
            new_layout.append({
                "position": position,
                "type": reference_type,
                "analysis_uid": new_analysis_uid,
                "container_uid": reference.UID()
            })
            workflow.doActionFor(analysis, "reject")
            analysis.reindexObject()
        # Duplicate analyses
        # - Create a new duplicate inside the new worksheet
        # - Transition the original analysis to 'rejected' state
        if api_analysis.is_duplicate_analysis(analysis):
            duplicate_id = new_ws.generateUniqueId("DuplicateAnalysis")
            new_duplicate = _createObjectByType("DuplicateAnalysis",
                                                new_ws, duplicate_id)
            new_duplicate.unmarkCreationFlag()
            copy_src_fields_to_dst(analysis, new_duplicate)
            new_duplicate.reindexObject()
            position = analysis_positions[analysis.UID()]
            old_ws_analyses.append(analysis.UID())
            old_layout.append({
                "position": position,
                "type": "d",
                "analysis_uid": analysis.UID(),
                "container_uid": worksheet.UID()
            })
            new_ws_analyses.append(new_duplicate.UID())
            new_layout.append({
                "position": position,
                "type": "d",
                "analysis_uid": new_duplicate.UID(),
                "container_uid": new_ws.UID()
            })
            workflow.doActionFor(analysis, "reject")
            analysis.reindexObject()

    new_ws.setAnalyses(new_ws_analyses)
    new_ws.setLayoutView(new_layout)
    for analysis in new_ws.getAnalyses():
        review_state = api.get_review_status(analysis)
        if review_state == "to_be_verified":
            # TODO Workflow - Analysis Retest transition within a Worksheet
            changeWorkflowState(analysis, ANALYSIS_WORKFLOW, "assigned")
    worksheet.REQUEST["context_uid"] = worksheet.UID()
    worksheet.setLayoutView(old_layout)
    worksheet.setAnalyses(old_ws_analyses)
