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


import json

from bika.lims import api
from bika.lims.api import snapshot as snap_api
from bika.lims.browser.fields.uidreferencefield import get_backreferences
from bika.lims.interfaces import IAuditable
from bika.lims.interfaces import IInvalidated
from bika.lims.utils import tmpID
from persistent.list import PersistentList
from plone.dexterity.utils import createContent
from Products.CMFEditions.interfaces import IVersioned
from senaite.core import logger
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.config import PROJECTNAME as product
from senaite.core.interfaces import IContentMigrator
from senaite.core.schema.uidreferencefield import get_backref_storage
from senaite.core.interfaces.catalog import ISenaiteCatalogObject
from senaite.core.setuphandlers import add_catalog_column
from senaite.core.setuphandlers import add_catalog_index
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from senaite.core.upgrade.utils import copy_snapshots
from senaite.core.upgrade.utils import delete_object
from senaite.core.upgrade.utils import remove_at_portal_types
from senaite.core.upgrade.utils import uncatalog_object
from senaite.core.upgrade.v02_06_000 import get_setup_folder
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

version = "2.7.0"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)

REMOVE_AT_TYPES = [
    "Calculation",
    "Calculations",
]


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


@upgradestep(product, version)
def import_rolemap(tool):
    """Import rolemap step from profiles
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup

    setup.runImportStepFromProfile(profile, "rolemap")


@upgradestep(product, version)
def import_registry(tool):
    """Import registry step from profiles
    """
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup

    setup.runImportStepFromProfile(profile, "plone.app.registry")


def mark_invalidated_samples(tool):
    """Mark invalidated samples with IInvalidated interface
    """
    logger.info("Mark invalidated samples as IInvalidated ...")
    query = {"portal_type": "AnalysisRequest", "review_state": "invalid"}
    brains = api.search(query, SAMPLE_CATALOG)
    total = len(brains)
    for num, brain in enumerate(brains):
        if num and num % 100 == 0:
            logger.info("Flagging invalidated samples {0}/{1}"
                        .format(num, total))

        sample = api.get_object(brain)
        if IInvalidated.providedBy(sample):
            continue

        alsoProvides(sample, IInvalidated)
        sample.reindexObject()
        sample._p_deactivate()

    logger.info("Mark invalidated samples as IInvalidated [DONE]")


@upgradestep(product, version)
def migrate_calculations_to_dx(tool):
    """Converts existing calculations to Dexterity
    """
    logger.info("Convert Calculations to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool, REMOVE_AT_TYPES)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")

    # get the old container
    origin = api.get_setup().get("bika_calculations")
    if not origin:
        # old container is already gone
        return

    # get the destination container
    destination = get_setup_folder("calculations")

    # un-catalog the old container
    uncatalog_object(origin)

    # copy items from old -> new container
    objects = origin.objectValues()
    for src in objects:
        migrate_calculation_to_dx(src, destination)

    # copy snapshots for the container
    copy_snapshots(origin, destination)

    # remove old AT folder
    if len(origin) == 0:
        delete_object(origin)
    else:
        logger.warn("Cannot remove {}. Is not empty".format(origin))

    remove_calculations_from_repositorytool()
    logger.info("Convert Calculations to Dexterity [DONE]")


def migrate_calculation_to_dx(src, destination=None):
    """Migrate an AT profile to DX in the destination folder

    :param src: The source AT object
    :param destination: The destination folder. If `None`, the parent folder of
                        the source object is taken
    """
    # migrate the contents from the old AT container to the new one
    portal_type = "Calculation"

    if api.get_portal_type(src) != portal_type:
        logger.error("Not a '{}' object: {}".format(portal_type, src))
        return

    # Create the object if it does not exist yet
    src_id = src.getId()
    target_id = src_id

    # check if we migrate within the same folder
    if destination is None:
        # use a temporary ID for the migrated content
        target_id = tmpID()
        # set the destination to the source parent
        destination = api.get_parent(src)

    target = destination.get(target_id)
    if not target:
        # Don' use the api to skip the auto-id generation
        target = createContent(portal_type, id=target_id)
        destination._setObject(target_id, target)
        target = destination._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = api.safe_unicode(src.Title() or "")
    target.description = api.safe_unicode(src.Description() or "")
    target.setPythonImports(src.getPythonImports() or [])
    target.setFormula(src.getFormula())
    target.setTestParameters(src.getTestParameters() or [])
    target.setTestResult(src.getTestResult() or "")
    target.setDependentServices(src.getDependentServices() or [])

    target_interims = []
    for src_interim in src.getInterimFields():
        interim = src_interim.copy()
        # ensure interim fields are unicode
        interim["unit"] = src_interim.get("unit") or ""
        interim["result_type"] = src_interim.get("result_type") or "numeric"
        interim["choices"] = src_interim.get("choices") or ""
        target_interims.append(interim)
    target.setInterimFields(target_interims)

    # Migrate the contents from AT to DX
    migrator = getMultiAdapter(
        (src, target), interface=IContentMigrator)

    # copy all (raw) attributes from the source object to the target
    migrator.copy_attributes(src, target)

    # copy the UID
    migrator.copy_uid(src, target)

    # create backrefs storage for newly created calculation and
    # move there uids of AnalisysServiced dependendent on this calc
    key = "CalculationDependentServices"
    src_backreferences = get_backreferences(src, relationship=key)
    target_storage = get_backref_storage(target)
    target_backrefs = target_storage[key] = PersistentList()
    for ref in src_backreferences:
        target_backrefs.append(api.get_uid(ref))

    # NOTE: We need to create the correct snapshot versions based on the stored
    # versions of the repository tool
    # migrator.copy_snapshots(src, target)
    pr = api.get_tool("portal_repository")
    for record in pr.getHistory(src, oldestFirst=True):
        # get the calculation object
        obj = record.object
        # create a snapshot for this object
        snapshot = snap_api.take_snapshot(obj, store=False)
        snapshot["__metadata__"].update({
            "actor": obj.Creator() or "migrator",
            "modified": obj.modified().ISO(),
            "snapshot_created": obj.created().ISO(),
            "comments": "Migrated snapshot from AT version {0}".format(
                record.version_id),
        })
        # store the snapshot on the target object
        storage = snap_api.get_storage(target)
        # append the JSON snapshot to the storage
        storage.append(json.dumps(snapshot))

    # provide the IAuditable interface to the target object
    alsoProvides(target, IAuditable)

    # disable the IVersioned interface on the source object
    if IVersioned.providedBy(src):
        noLongerProvides(src, IVersioned)

    # copy creators
    migrator.copy_creators(src, target)

    # copy workflow history
    migrator.copy_workflow_history(src, target)

    # copy marker interfaces
    migrator.copy_marker_interfaces(src, target)

    # copy dates
    migrator.copy_dates(src, target)

    # uncatalog the source object
    migrator.uncatalog_object(src)

    # delete the old object
    migrator.delete_object(src)

    # change the ID *after* the original object was removed
    migrator.copy_id(src, target)

    # We need to migrate all Analyses that linked to this Calculation!
    rc = api.get_tool("reference_catalog")
    refs = rc.getBackReferences(src, relationship="AnalysisCalculation")
    for ref in refs:
        analysis = ref.getSourceObject()
        if not analysis:
            # This can happen for Analyses in stale Samples, i.e. those with
            # with a temporary ID.
            logger.warn("Cannot migrate Analysis {}. No source object found."
                        .format(ref))
            continue
        analysis.setCalculation(target)
        analysis.deleteReferences(relationship="AnalysisCalculation")

    logger.info("Migrated Calculation from %s -> %s" % (src, target))


def remove_calculations_from_repositorytool():
    """Remove Analysis Service from Repository Tool
    """
    logger.info("Remove auto versioning for Calculations ...")
    portal_type = "Calculation"

    rt = api.get_tool("portal_repository")
    mapping = rt._version_policy_mapping
    mapping.pop(portal_type, None)
    rt._version_policy_mapping = mapping
    versionable_types = rt.getVersionableContentTypes()
    if portal_type in versionable_types:
        versionable_types.remove(portal_type)
        rt.setVersionableContentTypes(versionable_types)

    logger.info("Remove auto versioning for Calculation... [DONE]")


def upgrade_catalog_modified_index(tool):
    """Update modified index in catalog
    """
    logger.info("Upgrade catalog modified index ...")
    portal = api.get_portal()

    # Get all catalogs that implement ISenaiteCatalogObject
    objects = portal.objectValues()
    cats = [cat for cat in objects if ISenaiteCatalogObject.providedBy(cat)]

    # Add the `modified` index and metadata
    for cat in cats:
        add_catalog_index(cat, "modified", "", "DateIndex")
        add_catalog_column(cat, "modified")

    logger.info("Upgrade catalog modified index [DONE]")
    logger.warn(
        "You may need to manually reindex the 'modified' index in existing "
        "catalogs as required."
    )
