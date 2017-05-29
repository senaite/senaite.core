# This file is part of Bika LIMS
#
# Copyright 2011-2017 by it's authors.
# Some rights reserved. See LICENSE.txt, AUTHORS.txt.
from Acquisition import aq_inner
from Acquisition import aq_parent
from bika.lims import logger
from bika.lims.upgrade import upgradestep
from bika.lims.upgrade.utils import UpgradeUtils
from bika.lims.catalog import CATALOG_ANALYSIS_LISTING, \
    CATALOG_WORKSHEET_LISTING
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.config import VERSIONABLE_TYPES
from Products.CMFCore.utils import getToolByName
from bika.lims.upgrade.utils import migrate_to_blob
import traceback
import sys
import transaction
from plone.api.portal import get_tool

product = 'bika.lims'
version = '3.2.0.1705'


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

    # Remove duplicate attachments made by instrument imports
    remove_attachment_duplicates(portal, pgthreshold=1000)

    # Migrating ataip.FileField to blob.FileField
    migareteFileFields(portal)

    # Remove versionable types
    logger.info("Removing versionable types...")
    portal_repository = getToolByName(portal, 'portal_repository')
    non_versionable = ['AnalysisSpec',
                       'ARPriority',
                       'Method',
                       'SamplePoint',
                       'SampleType',
                       'StorageLocation',
                       'WorksheetTemplate', ]
    versionable = list(portal_repository.getVersionableContentTypes())
    vers = [ver for ver in versionable if ver not in non_versionable]
    portal_repository.setVersionableContentTypes(vers)
    logger.info("Versionable types updated: {0}".format(', '.join(vers)))

    # Add getId column to bika_catalog
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getNumberOfVerifications')
    # Add SearchableText index to analysis requests catalog
    ut.addIndex(
        CATALOG_ANALYSIS_REQUEST_LISTING, 'SearchableText', 'ZCTextIndex')
    # For reference samples
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getParentUID')
    ut.addColumn(CATALOG_ANALYSIS_LISTING, 'getDateSampled')

    # Reindexing bika_catalog_analysisrequest_listing in order to obtain the
    # correct getDateXXXs
    ut.addIndexAndColumn(
        CATALOG_ANALYSIS_REQUEST_LISTING, 'getDateVerified', 'DateIndex')
    if CATALOG_ANALYSIS_REQUEST_LISTING not in ut.refreshcatalog:
        ut.refreshcatalog.append(CATALOG_ANALYSIS_REQUEST_LISTING)

    # Refresh affected catalogs
    ut.refreshCatalogs()

    logger.info("{0} upgraded to version {1}".format(product, version))
    return True


def migareteFileFields(portal):
    """
    This function walks over all attachment types and migrates their FileField
    fields.
    """
    portal_types = [
        "Attachment",
        "ARImport",
        "Instrument",
        "InstrumentCertification",
        "Method",
        "Multifile",
        "Report",
        "ARReport",
        "SamplePoint"]
    for portal_type in portal_types:
        logger.info(
            "Starting migration of FileField fields from {}."
                .format(portal_type))
        # Do the migration
        migrate_to_blob(
            portal,
            portal_type=portal_type,
            remove_old_value=True)
        logger.info(
            "Finished migration of FileField fields from {}."
                .format(portal_type))


def remove_attachment_duplicates(portal, pgthreshold=1000):
    """Visit every worksheet attachment, and remove duplicates.
    The duplicates are filtered by filename, but that's okay because the
    instrument import routine used filenames when it made them.
    """
    pc = get_tool('portal_catalog')
    wc = get_tool(CATALOG_WORKSHEET_LISTING)

    # get all worksheets.
    brains = wc(portal_type='Worksheet')
    # list of lists.
    dup_ans = []  # [fn, primary attachment, duplicate attachment, worksheet]
    primaries = {}  # key is wsID:fn.  stores first found instance.
    # for each worksheet, get all attachments.
    dups_found = 0
    atts = []
    for brain in brains:
        ws = brain.getObject()
        ws_id = ws.getId()
        # for each attachment:
        atts = ws.objectValues('Attachment')
        for att in atts:
            # Only process each fn once:
            fn = att.getAttachmentFile().filename
            key = "%s:%s" % (ws_id, fn)
            if key in primaries:
                # we are a duplicate.
                dup_ans.append([fn, primaries[key], att, ws])
                dups_found += 1
                continue
            # not a dup.  att is primary attachment for this key.
            primaries[key] = att
    logger.info("Keeping {} and removing {} attachments".format(
        len(primaries), dups_found))

    # Now.
    count = 0
    for fn, att, dup, ws in dup_ans:
        # ans = [a for a in ws.getAnalyses() if dup.UID() in a.getAttachment()]
        ans = dup.getBackReferences()
        for an in ans:
            an.getField('Attachment').unset(an)
            an.setAttachment(att)
        path_uid = '/'.join(dup.getPhysicalPath())
        pc.uncatalog_object(path_uid)
        dup.aq_parent.manage_delObjects(dup.getId())
        #
        if count % pgthreshold == 0:
            logger.info("Removed {} of {} duplicate attachments...".format(
                count, dups_found))
        count += 1

