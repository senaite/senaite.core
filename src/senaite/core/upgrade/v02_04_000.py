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
# Copyright 2018-2022 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.interfaces import IRejected
from bika.lims.interfaces import IRetracted
from senaite.core import logger
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.config import PROJECTNAME as product
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from zope.interface import alsoProvides

version = "2.4.0"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # -------- ADD YOUR STUFF BELOW --------

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def reindex_qc_analyses(tool):
    """Reindex the QC analyses to ensure they are displayed again in worksheets

    :param tool: portal_setup tool
    """
    logger.info("Reindexing QC Analyses ...")
    query = {
        "portal_type": ["DuplicateAnalysis", "ReferenceAnalysis"],
        "review_state": "assigned",
    }
    brains = api.search(query, ANALYSIS_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Reindexed {0}/{1} QC analyses".format(num, total))

        obj = api.get_object(brain)
        obj.reindexObject(idxs=["getWorksheetUID", "getAnalyst"])

        # Flush the object from memory
        obj._p_deactivate()

    logger.info("Reindexing QC Analyses [DONE]")


def mark_retracted_and_rejected_analyses(tool):
    """Sets the IRetracted and/or IRejected interface to analyses that were
    either retracted or rejected
    :param tool: portal_setup tool
    """
    logger.info("Set IRetracted/IRejected interface to analyses ...")
    query = {
        "portal_type": ["Analysis", "ReferenceAnalysis", "DuplicateAnalysis"],
        "review_state": ["retracted", "rejected"],
    }
    brains = api.search(query, ANALYSIS_CATALOG)
    total = len(brains)

    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Set IRetracted/IRejected {0}/{1}".format(num, total))

        obj = api.get_object(brain)
        if IRetracted.providedBy(obj):
            obj._p_deactivate()  # noqa
            continue

        if IRejected.providedBy(obj):
            obj._p_deactivate()  # noqa
            continue

        status = api.get_review_status(obj)
        if status == "retracted":
            alsoProvides(obj, IRetracted)
        elif status == "rejected":
            alsoProvides(obj, IRejected)

    logger.info("Set IRetracted/IRejected interface to analyses [DONE]")


def fix_sample_actions_not_translated(tool):
    """Changes the name of the action item displayed in the actions list from
    sample (actbox) for the transitions 'submit' and 'receive'

    :param tool: portal_setup tool
    """
    logger.info("Fix sample actions without translation ...")
    actions = ["submit", "receive"]
    wf_tool = api.get_tool("portal_workflow")
    workflow = wf_tool.getWorkflowById("senaite_sample_workflow")
    for action in actions:
        transition = workflow.transitions.get(action)

        # update action with title
        transition.actbox_name = transition.title

    logger.info("Fix sample actions without translation [DONE]")


def fix_relative_path_stickers(tool):
    """Updates the actions from AnalysisRequest and ReferenceSample types so
    the absolute url for sticker icons is used instead of relative path
    """
    logger.info("Use portal as relative path for sticker icons ...")
    portal = api.get_portal()
    portal_types = ["AnalysisRequest", "ReferenceSample"]
    for portal_type in portal_types:
        type_info = portal.portal_types.getTypeInfo(portal_type)
        actions = type_info.listActions()
        for action in actions:
            icon_expr = action.getIconExpression() or ""
            if "senaite_theme/icon/" in icon_expr:
                icon = icon_expr.split("senaite_theme/icon/")[-1]
                icon_expr = "string:${portal_url}/senaite_theme/icon/%s" % icon
            action.setIconExpression(icon_expr)
    logger.info("Use portal as relative path for sticker icons [DONE]")