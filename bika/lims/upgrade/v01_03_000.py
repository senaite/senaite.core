# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE.rst, CONTRIBUTORS.rst.

from bika.lims import api
from bika.lims import logger
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils

version = '1.3.0'  # Remember version number in metadata.xml and setup.py
profile = 'profile-{0}:default'.format(product)

PORTLETS_TO_PURGE = [
    'accreditation-pt',
    'login',
    'news',
    'events',
    'Calendar',
    'portlet_department_filter-pt',
    'portlet_to_be_sampled-pt',
    'portlet_to_be_preserved-pt',
    'portlet_late_analyses-pt',
    'portlet_pending_orders-pt',
    'portlet_sample_due-pt',
    'portlet_to_be_verified-pt',
    'portlet_verified-pt'
]


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # -------- ADD YOUR STUFF BELOW --------

    # Remove QC reports and gpw dependency
    # https://github.com/senaite/senaite.core/pull/1058
    remove_qc_reports(portal)

    # Remove updates notification viewlet
    # https://github.com/senaite/senaite.core/pull/1059
    setup.runImportStepFromProfile(profile, 'viewlets')

    # Remove old portlets except the navigation portlet
    # https://github.com/senaite/senaite.core/pull/1060
    purge_portlets(portal)

    # Fix Cannot get the allowed transitions (guard_sample_prep_transition)
    # https://github.com/senaite/senaite.core/pull/1069
    remove_sample_prep_workflow(portal)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def remove_qc_reports(portal):
    """Removes the action Quality Control from Reports
    """
    logger.info("Removing Reports > Quality Control ...")
    ti = portal.reports.getTypeInfo()
    actions = map(lambda action: action.id, ti._actions)
    for index, action in enumerate(actions, start=0):
        if action == 'qualitycontrol':
            ti.deleteActions([index])
            break
    logger.info("Removing Reports > Quality Control [DONE]")


def purge_portlets(portal):
    """Remove old portlets. Leave the Navigation portlet only
    """
    logger.info("Purging portlets ...")

    def remove_portlets(context_portlet):
        mapping = portal.restrictedTraverse(context_portlet)
        for key in mapping.keys():
            if key not in PORTLETS_TO_PURGE:
                logger.info("Skipping portlet: '{}'".format(key))
                continue
            logger.info("Removing portlet: '{}'".format(key))
            del mapping[key]

    remove_portlets("++contextportlets++plone.leftcolumn")
    remove_portlets("++contextportlets++plone.rightcolumn")

    # Reimport the portlets profile
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, 'portlets')
    logger.info("Purging portlets [DONE]")


def remove_sample_prep_workflow(portal):
    """Removes sample_prep and sample_prep_complete transitions
    """
    # There is no need to walk through objects because of:
    # https://github.com/senaite/senaite.core/blob/master/bika/lims/upgrade/v01_02_008.py#L187
    logger.info("Removing 'sample_prep' related states and transitions ...")
    workflow_ids = ["bika_sample_workflow",
                    "bika_ar_workflow",
                    "bika_analysis_workflow"]
    to_remove = ["sample_prep", "sample_prep_complete"]
    wf_tool = api.get_tool("portal_workflow")
    for wf_id in workflow_ids:
        workflow = wf_tool.getWorkflowById(wf_id)
        for state_trans in to_remove:
            if state_trans in workflow.transitions:
                logger.info("Removing transition '{}' from '{}'"
                            .format(state_trans, wf_id))
                workflow.transitions.deleteTransitions([state_trans])
            if state_trans in workflow.states:
                logger.info("Removing state '{}' from '{}'"
                            .format(state_trans, wf_id))
                workflow.states.deleteStates([state_trans])
