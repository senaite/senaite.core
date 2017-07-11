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
from Products.CMFCore.utils import getToolByName
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING

from Products.CMFCore.Expression import Expression
from Products.CMFCore.utils import getToolByName

from bika.lims.catalog.report_catalog import bika_catalog_report_definition
from bika.lims.catalog.report_catalog import CATALOG_REPORT_LISTING

product = 'bika.lims'
version = '3.2.0.1707'


@upgradestep(product, version)
def upgrade(tool):
    portal = aq_parent(aq_inner(tool))
    setup = portal.portal_setup
    ut = UpgradeUtils(portal)
    ufrom = ut.getInstalledVersion(product)
    if ut.isOlderVersion(product, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            product, ufrom, version))
        # The currently installed version is more recent than the target
        # version of this upgradestep
        return True

    logger.info("Upgrading {0}: {1} -> {2}".format(product, ufrom, version))

    # importing toolset in order to add bika_catalog_report
    setup.runImportStepFromProfile('profile-bika.lims:default', 'toolset')

    # Renames some guard expressions from several transitions
    set_guard_expressions(portal)

    # Remove 'Date Published' from AR objects
    removeDatePublishedFromAR(portal)

    # Add missing Geo Columns to AR Catalog
    ut.addColumn(CATALOG_ANALYSIS_REQUEST_LISTING, 'getDistrict')
    ut.addColumn(CATALOG_ANALYSIS_REQUEST_LISTING, 'getProvince')

    create_report_catalog(portal, ut)
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

                    
def removeDatePublishedFromAR(portal):
    """
    DatePublished field has been removed from ARs' schema, because we didn't have setter and that field was always
    empty. Instead we are adding ComputedField which calls old getDatePublished() but is StringField.
    """
    uc = getToolByName(portal, 'uid_catalog')
    ars = uc(portal_type='AnalysisRequest')
    f_name = 'DatePublished'
    counter = 0
    tot_counter = 0
    total = len(ars)
    for ar in ars:
        obj = ar.getObject()
        if hasattr(obj, f_name):
            delattr(obj, f_name)
            counter += 1
        tot_counter += 1
        logger.info("Removing Date Published attribute from ARs: %d of %d" % (tot_counter, total))

    logger.info("'DatePublished' attribute has been removed from %d AnalysisRequest objects."
                % counter)


def create_report_catalog(portal, upgrade_utils):
    logger.info('Creating Report catalog')
    at = getToolByName(portal, 'archetype_tool')
    catalog_dict = bika_catalog_report_definition.get(CATALOG_REPORT_LISTING, {})
    report_indexes = catalog_dict.get('indexes', {})
    report_columns = catalog_dict.get('columns', [])
    # create report catalog indexes
    for idx in report_indexes:
        upgrade_utils.addIndex(CATALOG_REPORT_LISTING, idx, report_indexes[idx])
    # create report catalog columns
    for col in report_columns:
        upgrade_utils.addColumn(CATALOG_REPORT_LISTING, col)
    # define objects to be catalogued
    at.setCatalogsByType('Report', [CATALOG_REPORT_LISTING, ])
    # retrieve brains of objects to be catalogued from UID catalog
    logger.info('Recovering reports to reindex')
    bika_catalog = getToolByName(portal, 'bika_catalog')
    reports_brains = bika_catalog(portal_type='Report')
    i = 0  # already indexed objects counter
    # reindex the found objects in report catalog and uncatalog them from bika_catalog
    logger.info('Reindexing reports')
    for brain in reports_brains:
        if i % 100 == 0:
            logger.info('Reindexed {}/{} reports'.format(i, len(reports_brains)))
        report_obj = brain.getObject()
        report_obj.reindexObject()
        # uncatalog reports from bika_catalog
        path_uid = '/'.join(report_obj.getPhysicalPath())
        bika_catalog.uncatalog_object(path_uid)
        i += 1
    logger.info('Reindexed {}/{} reports'.format(len(reports_brains), len(reports_brains)))

