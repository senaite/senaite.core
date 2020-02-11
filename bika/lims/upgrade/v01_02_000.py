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

from bika.lims import logger, api
from bika.lims.catalog.analysis_catalog import CATALOG_ANALYSIS_LISTING
from bika.lims.config import PROJECTNAME as product
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from Products.CMFCore.Expression import Expression
from bika.lims.utils import changeWorkflowState

version = '1.2.0'  # Remember version number in metadata.xml and setup.py
profile = 'profile-{0}:default'.format(product)

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

    # -------- ADD YOUR STUFF HERE --------
    fix_workflow_transitions(portal)

    # Migration to senaite.core
    setup = portal.portal_setup
    setup.runImportStepFromProfile('profile-bika.lims:default', 'typeinfo')
    setup.runImportStepFromProfile('profile-bika.lims:default', 'propertiestool')
    rename_bika_setup()

    logger.info("{0} upgraded to version {1}".format(product, version))

    return True


def rename_bika_setup():
    logger.info("Renaming Bika Setup...")
    bika_setup = api.get_bika_setup()
    bika_setup.setTitle("Setup")
    bika_setup.reindexObject()


def fix_workflow_transitions(portal):
    """
    Replace target states from some workflow statuses
    """
    logger.info("Fixing workflow transitions...")
    tochange = [
        {'wfid': 'bika_duplicateanalysis_workflow',
         'trid': 'submit',
         'changes': {
             'new_state_id': 'to_be_verified',
             'guard_expr': ''
            },
         'update': {
             'catalog': CATALOG_ANALYSIS_LISTING,
             'portal_type': 'DuplicateAnalysis',
             'status_from': 'attachment_due',
             'status_to': 'to_be_verified'
            }
         }
    ]

    wtool = api.get_tool('portal_workflow')
    for item in tochange:
        wfid = item['wfid']
        trid = item['trid']
        workflow = wtool.getWorkflowById(wfid)
        transitions = workflow.transitions
        transition = transitions[trid]
        changes = item.get('changes', {})

        if 'new_state_id' in changes:
            new_state_id = changes['new_state_id']
            oldstate = transition.new_state_id
            logger.info(
                "Replacing target state '{0}' from '{1}.{2}' to {3}"
                    .format(oldstate, wfid, trid, new_state_id)
            )
            transition.new_state_id = new_state_id

        if 'guard_expr' in changes:
            new_guard = changes['guard_expr']
            if not new_guard:
                transition.guard = None
                logger.info(
                    "Removing guard expression from '{0}.{1}'"
                        .format(wfid, trid))
            else:
                guard = transition.getGuard()
                guard.expr = Expression(new_guard)
                transition.guard = guard
                logger.info(
                    "Replacing guard expression from '{0}.{1}' to {2}"
                        .format(wfid, trid, new_guard))

        update = item.get('update', {})
        if update:
            catalog_id = update['catalog']
            portal_type = update['portal_type']
            catalog = api.get_tool(catalog_id)
            brains = catalog(portal_type=portal_type)
            for brain in brains:
                obj = api.get_object(brain)
                if 'status_from' in update and 'status_to' in update:
                    status_from = update['status_from']
                    status_to = update['status_to']
                    if status_from == brain.review_state:
                        logger.info(
                            "Changing status for {0} from '{1} to {2}"
                                .format(obj.getId(), status_from, status_to))
                        changeWorkflowState(obj, wfid, status_to)

                workflow.updateRoleMappingsFor(obj)
                obj.reindexObject()
