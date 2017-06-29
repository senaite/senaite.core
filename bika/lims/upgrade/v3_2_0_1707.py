# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Acquisition import aq_inner
from Acquisition import aq_parent

from bika.lims import logger
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from plone.api.portal import get_tool
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING

from Products.CMFCore.Expression import Expression

product = 'bika.lims'
version = '3.2.0.1707'


@upgradestep(product, version)
def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    ut = UpgradeUtils(portal)
    ufrom = ut.getInstalledVersion(product)
    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ufrom, version))
        # The currently installed version is more recent than the target
        # version of this upgradestep
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ufrom, version))

    # Renames some guard expressions from several transitions
    set_guard_expressions(portal)

    # Result per sample report improved
    result_per_sample_index_and_cols(ut)
    ut.refreshCatalogs()
    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def set_guard_expressions(portal):
    """Rename guard expressions of some workflow transitions
    """
    logger.info('Renaming guard expressions...')
    torename = {
        'bika_ar_workflow.publish': 'python:here.guard_publish_transition()',
    }
    wtool = get_tool('portal_workflow')
    workflowids = wtool.getWorkflowIds()
    for wfid in workflowids:
        workflow = wtool.getWorkflowById(wfid)
        transitions = workflow.transitions
        for transid in transitions.objectIds():
            for torenid, newguard in torename.items():
                tokens = torenid.split('.')
                if tokens[0] == wfid and tokens[1] == transid:
                    transition = transitions[transid]
                    guard = transition.getGuard()
                    guard.expr = Expression(newguard)
                    transition.guard = guard
                    logger.info("Guard from transition '{0}' set to '{1}'"
                                .format(torenid, newguard))

def result_per_sample_index_and_cols(ut):
    """
    Adding indexes and columns in analyses catalog in order to
    render that report as fast as possible.
    """
    ut.addIndex(
        CATALOG_ANALYSIS_LISTING,
        'getSampleID',
        'FieldIndex',
        )
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getFormattedResult')
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getSampleID')
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getSampleTypeID')
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getClientReference')
