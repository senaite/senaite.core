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

import time
from collections import OrderedDict

import transaction
from Acquisition import aq_base
from Products.DCWorkflow.States import StateDefinition
from Products.DCWorkflow.events import AfterTransitionEvent
from bika.lims import api
from bika.lims import logger
from bika.lims import permissions
from bika.lims.api import get_object, get_review_status, get_workflows_for
from bika.lims.config import PROJECTNAME as product
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.utils import changeWorkflowState
from zope.event import notify

version = '1.2.8'  # Remember version number in metadata.xml and setup.py
profile = 'profile-{0}:default'.format(product)


@upgradestep(product, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(product)
    setup = portal.portal_setup

    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ver_from, version))
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ver_from, version))

    # -------- ADD YOUR STUFF HERE --------

    setup.runImportStepFromProfile(profile, 'catalog')
    setup.runImportStepFromProfile(profile, 'workflow')

    # Revert upgrade actions performed due to #893 (reverted)
    revert_client_permissions_for_batches(portal)

    # re-apply the permission for the view tabs on clients
    setup.runImportStepFromProfile(profile, 'typeinfo')
    # re-apply the permissions from the client workflow + reindex
    fix_client_permissions(portal)

    fix_items_stuck_in_sample_prep_states(portal, ut)

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def get_workflows():
    """Returns a mapping of id->workflow
    """
    wftool = api.get_tool("portal_workflow")
    wfs = {}
    for wfid in wftool.objectIds():
        wf = wftool.getWorkflowById(wfid)
        if hasattr(aq_base(wf), "updateRoleMappingsFor"):
            wfs[wfid] = wf
    return wfs


def update_role_mappings(obj, wfs=None, reindex=True):
    """Update the role mappings of the given object
    """
    wftool = api.get_tool("portal_workflow")
    if wfs is None:
        wfs = get_workflows()
    chain = wftool.getChainFor(obj)
    for wfid in chain:
        wf = wfs[wfid]
        wf.updateRoleMappingsFor(obj)
    if reindex is True:
        obj.reindexObject(idxs=["allowedRolesAndUsers"])
    return obj


def fix_client_permissions(portal):
    """Fix client permissions
    """
    wfs = get_workflows()

    start = time.time()
    clients = portal.clients.objectValues()
    total = len(clients)
    for num, client in enumerate(clients):
        logger.info("Fixing permission for client {}/{} ({})"
                    .format(num, total, client.getName()))
        update_role_mappings(client, wfs=wfs)
    end = time.time()
    logger.info("Fixing client permissions took %.2fs" % float(end-start))
    transaction.commit()


def revert_client_permissions_for_batches(portal):
    mp = portal.batches.manage_permission
    mp(permissions.View, ['Manager', 'LabManager', 'LabClerk', 'Analyst', 'RegulatoryInspector'], 0)
    portal.batches.reindexObject()

    wftool = api.get_tool("portal_workflow")
    batch_wf = wftool.getWorkflowById("bika_batch_workflow")
    acquire = False

    grant = ['Analyst', 'LabClerk', 'LabManager', 'Manager', 'RegulatoryInspector', 'Verifier']
    batch_wf.states.open.setPermission("View", acquire, grant)

    grant = ['LabClerk', 'LabManager', 'Manager', 'RegulatoryInspector']
    batch_wf.states.closed.setPermission("View", acquire, grant)

    catalog = api.get_tool('portal_catalog')
    brains = catalog(portal_type='Batch', allowedRolesAndUsers=["Client"])
    for brain in brains:
        obj = api.get_object(brain)
        batch_wf.updateRoleMappingsFor(obj)
        obj.reindexObject(idxs=['allowedRolesAndUsers'])
        logger.info("Role mappings updated for {}".format(obj))


def fix_ar_sample_workflow(brain_or_object):
    """Re-set the state of an AR, Sample and SamplePartition to match the
    least-early state of all contained valid/current analyses. Ignores
    retracted/rejected/cancelled analyses.
    """

    def log_change_state(ar_id, obj_id, src, dst):
        msg = "While fixing {ar_id}: " \
              "state changed for {obj_id}: " \
              "{src} -> {dst}".format(**locals())

    ar = get_object(brain_or_object)
    if not IAnalysisRequest.providedBy(ar):
        return

    wf = api.get_tool('portal_workflow')
    arwf = wf['bika_ar_workflow']
    anwf = wf['bika_analysis_workflow']
    swf = wf['bika_sample_workflow']
    ignored = ['retracted', 'rejected']

    tmp = filter(lambda x: x[0] not in ignored, arwf.states.items())
    arstates = OrderedDict(tmp)
    tmp = filter(lambda x: x[0] not in ignored, swf.states.items())
    samplestates = OrderedDict(tmp)
    tmp = filter(lambda x: x[0] in arstates, anwf.states.items())
    anstates = OrderedDict(tmp)

    # find least-early analysis state
    # !!! Assumes states in definitions are roughly ordered earliest to latest
    ar_dest_state = arstates.items()[0][0]
    for anstate in anstates:
        if ar.getAnalyses(review_state=anstate):
            ar_dest_state = anstate

    # Force state of AR
    ar_state = get_review_status(ar)
    if ar_state != ar_dest_state:
        changeWorkflowState(ar, arwf.id, ar_dest_state)
        log_change_state(ar.id, ar.id, ar_state, ar_dest_state)

    # Force state of Sample
    sample = ar.getSample()
    sample_state = get_review_status(sample)
    if ar_dest_state in samplestates:
        changeWorkflowState(sample, swf.id, ar_dest_state)
        log_change_state(ar.id, sample.id, sample_state, ar_dest_state)

        # Force states of Partitions
        for part in sample.objectValues():
            part_state = get_review_status(part)
            if get_review_status(part) != ar_dest_state:
                changeWorkflowState(sample, swf.id, ar_dest_state)
                log_change_state(ar.id, part.id, part_state, ar_dest_state)


def fix_items_stuck_in_sample_prep_states(portal, ut):
    """Removing sample preparation workflows from the system may have
    left some samples ARs and Analyses in the state 'sample_prep'.  These
    should be transitioned to 'sample_due'  so that they can be receieved
    normally.
    :param portal: portal object
    :return: None
    """
    wftool = api.get_tool('portal_workflow')
    catalog_ids = ['bika_catalog',
                   'bika_analysis_catalog',
                   'bika_catalog_analysisrequest_listing']
    for catalog_id in catalog_ids:
        catalog = api.get_tool(catalog_id)
        brains = catalog(review_state='sample_prep')
        for brain in brains:
            instance = brain.getObject()
            wfid = get_workflows_for(instance)[0]
            wf = wftool[wfid]
            # get event properties for last event that is not sample_prep
            rh = wftool.getInfoFor(instance, 'review_history')
            event = [x for x in rh if 'prep' not in x['review_state']
                     and not x['comments']][-1]
            state_id, action_id = event['review_state'], event['action']
            # set state
            changeWorkflowState(instance, wfid, state_id)
            # fire transition handler for the action that originally was fired.
            old_sdef = new_sdef = wf.states[state_id]
            if action_id is not None:
                tdef = wf.transitions[action_id]
                notify(AfterTransitionEvent(
                    instance, wf, old_sdef, new_sdef, tdef, event, {}))
            # check AR state matches the analyses
            if IAnalysisRequest.providedBy(instance):
                fix_ar_sample_workflow(instance)
        logger.info("Removed sample_prep state from {} items in {}."
                    .format(len(brains), catalog_id))
