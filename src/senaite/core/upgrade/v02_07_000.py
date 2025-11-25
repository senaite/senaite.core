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


from bika.lims import api
from bika.lims.api import safe_unicode as u
from bika.lims.interfaces import IInvalidated
from bika.lims.utils import tmpID
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import createContent
from senaite.core import logger
from senaite.core.catalog import ANALYSIS_CATALOG
from senaite.core.catalog import CONTACT_CATALOG
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.catalog.analysis_catalog import INDEXES as ANALYSIS_INDEXES
from senaite.core.config import PROJECTNAME as product
from senaite.core.interfaces import IContentMigrator
from senaite.core.interfaces.catalog import ISenaiteCatalogObject
from senaite.core.schema.addressfield import NAIVE_ADDRESS
from senaite.core.schema.addressfield import PHYSICAL_ADDRESS
from senaite.core.schema.addressfield import POSTAL_ADDRESS
from senaite.core.setuphandlers import _run_import_step
from senaite.core.setuphandlers import add_catalog_column
from senaite.core.setuphandlers import add_catalog_index
from senaite.core.setuphandlers import add_dexterity_items
from senaite.core.setuphandlers import setup_core_catalogs
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

version = "2.7.0"  # Remember version number in metadata.xml and setup.py
profile = "profile-{0}:default".format(product)

REMOVE_AT_TYPES = [
    "Contact",
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

    # XXX: The plone.app.registry step depends on the typeinfo step, which
    # causes this error if executed w/o AT portal type removal first:
    #
    # Traceback (innermost last):
    #   Module ZPublisher.WSGIPublisher, line 176, in transaction_pubevents
    #   Module ZPublisher.WSGIPublisher, line 385, in publish_module
    #   Module ZPublisher.WSGIPublisher, line 288, in publish
    #   Module ZPublisher.mapply, line 85, in mapply
    #   Module ZPublisher.WSGIPublisher, line 63, in call_object
    #   Module Products.GenericSetup.tool, line 1135, in manage_doUpgrades
    #   Module Products.GenericSetup.upgrade, line 185, in doStep
    #   Module senaite.core.upgrade, line 39, in wrap_func_args
    #   Module senaite.core.upgrade.v02_07_000, line 86, in import_registry
    #   Module Products.GenericSetup.tool, line 375, in runImportStepFromProfile
    #   Module Products.GenericSetup.tool, line 1323, in _doRunImportStep
    #    - __traceback_info__: typeinfo
    #   Module Products.CMFCore.exportimport.typeinfo, line 222, in importTypesTool
    #   Module Products.GenericSetup.utils, line 934, in importObjects
    #    - __traceback_info__: portal_types
    #   Module Products.GenericSetup.utils, line 930, in importObjects
    #    - __traceback_info__: types/Contact
    #   Module Products.GenericSetup.utils, line 530, in _importBody
    #   Module Products.CMFCore.exportimport.typeinfo, line 61, in _importNode
    #   Module Products.GenericSetup.utils, line 763, in _initProperties
    # ValueError: undefined property 'add_permission'
    remove_at_portal_types(tool)

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


def update_analysis_catalog_indexes(tool):
    """Update analysis catalog indexes
    """
    logger.info("Update analysis catalog indexes ...")
    to_reindex = []
    catalog = api.get_tool(ANALYSIS_CATALOG)
    for record in ANALYSIS_INDEXES:
        if add_catalog_index(catalog, *record):
            to_reindex.append(record[0])

    for index_id in to_reindex:
        logger.info("Reindexing index '%s'" % index_id)
        catalog.reindexIndex(index_id, api.get_request())

    logger.info("Update analysis catalog indexes [DONE]")


def remove_at_portal_types(tool):
    """Remove obsolete AT portal type information
    """
    logger.info("Remove AT types from portal_types tool ...")
    pt = api.get_tool("portal_types")
    for type_name in REMOVE_AT_TYPES:
        fti = pt.getTypeInfo(type_name)
        # keep DX FTIs
        if isinstance(fti, DexterityFTI):
            logger.info("Type '{}' is already a DX FTI".format(fti))
            continue
        elif not fti:
            # Removed already
            continue
        pt.manage_delObjects(fti.getId())

    # remove from AT's factory tool as well. This is necessary for the AT's
    # factory_tool to not shortcut `createObject?type_name=` on object creation
    ft = api.get_tool("portal_factory")
    at_types = ft.getFactoryTypes().keys()
    at_types = filter(lambda name: name not in REMOVE_AT_TYPES, at_types)
    ft.manage_setPortalFactoryTypes(listOfTypeIds=at_types)

    logger.info("Remove AT types from portal_types tool ... [DONE]")


def migrate_contacts_to_dx(tool):
    """Migrate Contact objects from Archetypes to Dexterity
    """
    logger.info("Migrating Contacts to Dexterity ...")

    # Ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")

    # Find all Contact objects (excluding LabContact and SupplierContact)
    query = {
        "portal_type": "Contact",
    }
    brains = api.search(query, CONTACT_CATALOG)
    total = len(brains)
    logger.info("Found {} Contact objects to migrate".format(total))

    for num, brain in enumerate(brains, start=1):
        # Get the object
        contact = api.get_object(brain)

        if num % 100 == 0:
            logger.info("Progress: {}/{} contacts migrated".format(num, total))

        # Skip if already migrated to Dexterity
        if not api.is_at_content(contact):
            logger.info("[{}/{}] Already migrated: {}".format(
                num, total, api.get_path(contact)))
            continue

        migrate_contact_to_dx(contact)

    logger.info("Migrating Contacts to Dexterity [DONE]")


def migrate_contact_to_dx(src, destination=None):
    """Migrate an AT contact to DX in the destination folder

    :param src: The source AT object
    :param destination: The destination folder. If `None`, the parent folder of
                        the source object is taken
    """
    # migrate the contents from the old AT container to the new one
    portal_type = "Contact"

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
        # Don't use the api to skip the auto-id generation
        target = createContent(portal_type, id=target_id)
        destination._setObject(target_id, target)
        target = destination._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = u""  # calculated
    target.description = u""  # not used
    target.salutation = api.safe_unicode(src.getSalutation() or "")
    target.firstname = api.safe_unicode(src.getFirstname() or "")
    target.middleinitial = api.safe_unicode(src.getMiddleinitial() or "")
    target.middlename = api.safe_unicode(src.getMiddlename() or "")
    target.surname = api.safe_unicode(src.getSurname() or "")
    target.username = api.safe_unicode(src.getUsername() or "")
    target.email_address = api.safe_unicode(src.getEmailAddress() or "")
    target.business_phone = api.safe_unicode(src.getBusinessPhone() or "")
    target.business_fax = api.safe_unicode(src.getBusinessFax() or "")
    target.home_phone = api.safe_unicode(src.getHomePhone() or "")
    target.mobile_phone = api.safe_unicode(src.getMobilePhone() or "")
    target.job_title = api.safe_unicode(src.getJobTitle() or "")
    target.department = api.safe_unicode(src.getDepartment() or "")
    target.cc_contact = src.getRawCCContact() or []

    # NOTE: Addresses behave differently in AT and DX
    physical_address = src.getPhysicalAddress() or {}
    if physical_address:
        address = to_dx_address(physical_address, PHYSICAL_ADDRESS)
        target.setPhysicalAddress(address)

    postal_address = src.getPostalAddress() or {}
    if postal_address:
        address = to_dx_address(postal_address, POSTAL_ADDRESS)
        target.setPostalAddress(address)

    # Migrate the contents from AT to DX
    migrator = getMultiAdapter(
        (src, target), interface=IContentMigrator)

    # copy all (raw) attributes from the source object to the target
    migrator.copy_attributes(src, target)

    # copy the UID
    migrator.copy_uid(src, target)

    # copy auditlog
    migrator.copy_snapshots(src, target)

    # copy creators
    migrator.copy_creators(src, target)

    # copy workflow history
    migrator.copy_workflow_history(src, target)

    # copy marker interfaces
    migrator.copy_marker_interfaces(src, target)

    # copy dates
    migrator.copy_dates(src, target)

    # move eventual contents from source to target
    if api.is_folderish(src):
        cp = src.manage_cutObjects(ids=src.objectIds())
        target.manage_pasteObjects(cp)

    # uncatalog the source object
    migrator.uncatalog_object(src)

    # delete the old object
    migrator.delete_object(src)

    # change the ID *after* the original object was removed
    migrator.copy_id(src, target)

    logger.info("Migrated Contact from %s -> %s" % (src, target))


def to_dx_address(value, address_type=NAIVE_ADDRESS):
    return {
        "type": u(value.get("address_type") or address_type),
        "address": u(value.get("address") or ""),
        "zip": u(value.get("zip") or ""),
        "city": u(value.get("city") or ""),
        "subdivision1": u(value.get("state") or ""),
        "subdivision2": u(value.get("district") or ""),
        "country": u(value.get("country") or ""),
    }


def create_setup_contacts_folder(tool):
    """Create the Contacts container in the setup folder
    """
    logger.info("Creating Contacts container in setup folder ...")

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "actions")

    setup = api.get_senaite_setup()

    # Check if contacts folder already exists
    if not setup.get("contacts"):
        items = [("contacts", "Contacts", "Contacts")]
        add_dexterity_items(setup, items)
        logger.info("Contacts container created")
    else:
        logger.info("Contacts folder already exists [SKIP]")

    logger.info("Creating Contacts container in setup folder [DONE]")


@upgradestep(product, version)
def setup_custom_image_and_file_types(tool):
    """Setup custom File and Image types and add Attachments catalog
    """
    logger.info("Setup custom File and Image types ...")
    portal = tool.aq_inner.aq_parent
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")
    # Needed for the updated Client.xml action
    _run_import_step(portal, "typeinfo", "profile-bika.lims:default")
    setup_core_catalogs(portal)
    logger.info("Setup custom File and Image types [DONE]")
