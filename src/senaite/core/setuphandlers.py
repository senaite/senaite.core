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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from Acquisition import aq_base
from bika.lims import api
from bika.lims.setuphandlers import reindex_content_structure
from bika.lims.setuphandlers import setup_form_controller_actions
from bika.lims.setuphandlers import setup_groups
from plone.dexterity.fti import DexterityFTI
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.utils import get_installer
from Products.GenericSetup.utils import _resolveDottedName
from senaite.core import logger
from senaite.core.api.catalog import add_column
from senaite.core.api.catalog import add_index
from senaite.core.api.catalog import del_column
from senaite.core.api.catalog import del_index
from senaite.core.api.catalog import get_columns
from senaite.core.api.catalog import get_indexes
from senaite.core.api.catalog import reindex_index
from senaite.core.catalog import AUDITLOG_CATALOG
from senaite.core.catalog import CATALOG_MAPPINGS
from senaite.core.catalog import AnalysisCatalog
from senaite.core.catalog import AuditlogCatalog
from senaite.core.catalog import AutoImportLogCatalog
from senaite.core.catalog import ClientCatalog
from senaite.core.catalog import ContactCatalog
from senaite.core.catalog import LabelCatalog
from senaite.core.catalog import ReportCatalog
from senaite.core.catalog import SampleCatalog
from senaite.core.catalog import SenaiteCatalog
from senaite.core.catalog import SetupCatalog
from senaite.core.catalog import WorksheetCatalog
from senaite.core.config import PROFILE_ID
from senaite.core.upgrade.utils import temporary_allow_type
from zope.component import getUtility
from zope.interface import implementer

try:
    from Products.CMFPlone.interfaces import IMarkupSchema
    from Products.CMFPlone.interfaces import INonInstallable
except ImportError:
    from zope.interface import Interface
    IMarkupSchema = None

    class INonInstallable(Interface):
        pass


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide all profiles from site-creation and quickinstaller (not ZMI)"""
        return [
            # Leave visible to allow upgrade via the Plone Add-on controlpanel
            # "bika.lims:default",

            # hide install profiles that come with Plone
            "Products.CMFPlacefulWorkflow:CMFPlacefulWorkflow",
            "Products.CMFPlacefulWorkflow:base",
            "Products.CMFPlacefulWorkflow:uninstall",
            "Products.DataGridField:default",
            "Products.DataGridField:example",
            "Products.TextIndexNG3:default",
            "archetypes.multilingual:default",
            "archetypes.referencebrowserwidget:default",
            "collective.js.jqueryui:default"
            "plone.app.iterate:default",
            "plone.app.iterate:plone.app.iterate",
            "plone.app.iterate:test",
            "plone.app.iterate:uninstall",
            "plone.app.jquery:default",
            "plonetheme.barceloneta:default",
        ]


CONTENTS_TO_DELETE = (
    # List of items to delete
    "Members",
    "news",
    "events",
)

CATALOGS = (
    AnalysisCatalog,
    AuditlogCatalog,
    AutoImportLogCatalog,
    ClientCatalog,
    ContactCatalog,
    LabelCatalog,
    ReportCatalog,
    SampleCatalog,
    SenaiteCatalog,
    SetupCatalog,
    WorksheetCatalog,
)

INDEXES = (
    # catalog, id, indexed attribute, type
    ("uid_catalog", "path", "getPhysicalPath", "ExtendedPathIndex"),
)

COLUMNS = (
    # catalog, column name
)

REMOVE_PORTAL_CATALOG_INDEXES = (
    "Analyst",
    "SearchableText",
    "commentators",
    "getName",
    "getParentUID",
    "getRawRelatedItems",
    "getUsername",
    "in_reply_to",
    "sync_uid",
    "total_comments",
)

REMOVE_PORTAL_CATALOG_COLUMNS = (
    "Analyst",
    "analysisRequestTemplates",
    "author_name",
    "cmf_uid",
    "commentators",
    "getClientID",
    "in_response_to",
    "last_comment_date",
    "sync_uid",
    "total_comments",
)


def install(context):
    """Install handler
    """
    if context.readDataFile("senaite.core.txt") is None:
        return

    logger.info("SENAITE CORE install handler [BEGIN]")
    portal = context.getSite()

    # Run required import steps
    _run_import_step(portal, "skins")
    _run_import_step(portal, "browserlayer")
    _run_import_step(portal, "rolemap")
    _run_import_step(portal, "typeinfo")
    _run_import_step(portal, "factorytool")
    _run_import_step(portal, "workflow", "profile-senaite.core:default")
    _run_import_step(portal, "typeinfo", "profile-senaite.core:default")

    # skip installers if already installed
    qi = get_installer(portal)
    profiles = ["bika.lims", "senaite.core"]
    if any(map(lambda p: qi.is_product_installed(p), profiles)):
        logger.info("SENAITE CORE already installed [SKIP]")
        return

    # Run Installers
    setup_groups(portal)
    remove_default_content(portal)
    # setup catalogs
    setup_portal_catalog(portal)
    setup_core_catalogs(portal)
    setup_other_catalogs(portal)
    setup_catalog_mappings(portal)
    setup_auditlog_catalog_mappings(portal)
    setup_catalogs_order(portal)
    setup_content_structure(portal)
    add_senaite_setup(portal)
    add_senaite_setup_items(portal)
    add_dexterity_portal_items(portal)

    # Set CMF Form actions
    setup_form_controller_actions(portal)
    setup_form_controller_more_action(portal)

    # Setup markup default and allowed schemas
    setup_markup_schema(portal)

    logger.info("SENAITE CORE install handler [DONE]")


def add_senaite_setup(portal):
    """Add the new SENAITE Setup container
    """
    items = [
        # ID, Title, FTI
        ("setup", "SENAITE Setup", "Setup"),
    ]
    add_dexterity_items(portal, items)

    # Move Setup at the beginning
    portal.moveObjectToPosition("setup", 0)

    # Reindex order
    portal.plone_utils.reindexOnReorder(portal)


def add_senaite_setup_items(portal):
    """Adds setup items to the new SENAITE setup
    """
    items = [
        # ID, Title, FTI
        ("departments", "Lab Departments", "Departments"),
        ("labels", "Labels", "Labels"),
        ("sampleconditions", "Sample Conditions", "SampleConditions"),
        ("analysisprofiles", "Analysis Profiles", "AnalysisProfiles"),
        ("samplepreservations", "Sample Preservations", "SamplePreservations"),
        ("samplematrices", "Sample Matrices", "SampleMatrices"),
        ("samplepoints", "Sample Points", "SamplePoints"),
        ("sampletemplates", "Sample Templates", "SampleTemplates"),
        ("manufacturers", "Manufacturers", "Manufacturers"),
        ("containertypes", "Container Types", "ContainerTypes"),
        ("subgroups", "SubGroups", "SubGroups"),
        ("storagelocations", "Storage Locations", "StorageLocations"),
        ("instrumenttypes", "Instrument Types", "InstrumentTypes"),
        ("samplingdeviations", "Sampling Deviations", "SamplingDeviations"),
        ("batchlabels", "Batch Labels", "BatchLabels"),
        ("analysiscategories", "Analysis Categories", "AnalysisCategories"),
        ("instrumentlocations", "Instrument Locations", "InstrumentLocations"),
        ("samplecontainers", "Sample Containers", "SampleContainers"),
        ("attachmenttypes", "Attachment Types", "AttachmentTypes"),
        ("dynamicanalysisspecs", "Dynamic Analysis Specifications",
         "DynamicAnalysisSpecs"),
        ("interpretationtemplates", "Interpretation Templates",
         "InterpretationTemplates"),
        ("labproducts", "Lab Products", "LabProducts"),
        ("suppliers", "Suppliers", "Suppliers"),
        ("sampletypes", "Sample Types", "SampleTypes"),
        ("worksheettemplates", "Worksheet Templates", "WorksheetTemplates"),
    ]
    setup = api.get_senaite_setup()
    add_dexterity_items(setup, items)


def add_dexterity_portal_items(portal):
    """Adds the Dexterity Container in the Site folder

    N.B.: We do this in code, because adding this as Generic Setup Profile in
          `profiles/default/structure` flushes the contents on every import.
    """
    # Tuples of ID, Title, FTI
    items = [
        # ID, Title, FTI
        ("samples", "Samples", "Samples"),
    ]
    add_dexterity_items(portal, items)

    # Move Samples after Clients nav item
    position = portal.getObjectPosition("clients")
    portal.moveObjectToPosition("samples", position + 1)

    # Reindex order
    portal.plone_utils.reindexOnReorder(portal)


def add_dexterity_items(container, items):
    """Adds a dexterity item, usually a folder in the container
    :param container: container of the items to add
    :param items: tuple of Id, Title, FTI
    """
    for id, title, fti in items:
        obj = container.get(id)
        if obj is None:
            with temporary_allow_type(container, fti) as ct:
                obj = api.create(ct, fti, id=id, title=title)
        else:
            obj.setTitle(title)
        obj.reindexObject()


def setup_portal_catalog(portal):
    """Remove all unneeded indexes
    """
    logger.info("*** Setup portal catalog ***")

    catalog = api.get_tool("portal_catalog")
    indexes = get_indexes(catalog)
    for index in indexes:
        if index in REMOVE_PORTAL_CATALOG_INDEXES:
            logger.info("*** Removing index '%s' from catalog '%s'"
                        % (index, catalog.id))
            # remove index
            del_index(catalog, index)

    columns = get_columns(catalog)
    for column in columns:
        if column in REMOVE_PORTAL_CATALOG_COLUMNS:
            logger.info("*** Removing column '%s' from catalog '%s'"
                        % (column, catalog.id))
            # remove column
            del_column(catalog, column)


def setup_core_catalogs(portal, catalog_classes=None, reindex=True):
    """Setup core catalogs
    """
    logger.info("*** Setup core catalogs ***")
    at = api.get_tool("archetype_tool")

    # allow add-ons to use this handler with own catalogs
    if catalog_classes is None:
        catalog_classes = CATALOGS

    # contains tuples of (catalog, index) pairs
    to_reindex = []

    for cls in catalog_classes:
        module = _resolveDottedName(cls.__module__)

        # get the required attributes from the module
        catalog_id = module.CATALOG_ID
        catalog_indexes = module.INDEXES
        catalog_columns = module.COLUMNS
        catalog_types = module.TYPES

        catalog = getattr(aq_base(portal), catalog_id, None)
        if catalog is None:
            catalog = cls()
            catalog._setId(catalog_id)
            portal._setObject(catalog_id, catalog)

        # catalog indexes
        for idx_id, idx_attr, idx_type in catalog_indexes:
            if add_catalog_index(catalog, idx_id, idx_attr, idx_type):
                to_reindex.append((catalog, idx_id))
            else:
                continue

        # catalog columns
        for column in catalog_columns:
            add_catalog_column(catalog, column)

        if not reindex:
            logger.info("*** Skipping reindex of new indexes")
            return

        # map allowed types to this catalog in archetype_tool
        for portal_type in catalog_types:
            # check existing catalogs
            catalogs = at.getCatalogsByType(portal_type)
            if catalog not in catalogs:
                existing = list(map(lambda c: c.getId(), catalogs))
                new_catalogs = existing + [catalog_id]
                at.setCatalogsByType(portal_type, new_catalogs)
                logger.info("*** Mapped catalog '%s' for type '%s'"
                            % (catalog_id, portal_type))

    # reindex new indexes
    for catalog, idx_id in to_reindex:
        reindex_catalog_index(catalog, idx_id)


def setup_other_catalogs(portal, indexes=None, columns=None):
    logger.info("*** Setup other catalogs ***")

    # contains tuples of (catalog, index) pairs
    to_reindex = []

    # allow add-ons to use this handler with other index/column definitions
    if indexes is None:
        indexes = INDEXES
    if columns is None:
        columns = COLUMNS

    # catalog indexes
    for catalog, idx_id, idx_attr, idx_type in indexes:
        catalog = api.get_tool(catalog)
        if add_catalog_index(catalog, idx_id, idx_attr, idx_type):
            to_reindex.append((catalog, idx_id))
        else:
            continue

    # catalog columns
    for catalog, column in columns:
        catalog = api.get_tool(catalog)
        add_catalog_column(catalog, column)

    # reindex new indexes
    for catalog, idx_id in to_reindex:
        reindex_catalog_index(catalog, idx_id)


def reindex_catalog_index(catalog, index):
    catalog_id = catalog.id
    logger.info("*** Indexing new index '%s' in '%s' ..."
                % (index, catalog_id))
    reindex_index(catalog, index)
    logger.info("*** Indexing new index '%s' in '%s' [DONE]"
                % (index, catalog_id))


def add_catalog_index(catalog, idx_id, idx_attr, idx_type):
    indexes = get_indexes(catalog)
    # check if the index exists
    if idx_id in indexes:
        logger.info("*** %s '%s' already in catalog '%s'"
                    % (idx_type, idx_id, catalog.id))
        return False
    # create the index
    add_index(catalog, idx_id, idx_type, indexed_attrs=idx_attr)
    logger.info("*** Added %s '%s' for catalog '%s'"
                % (idx_type, idx_id, catalog.id))
    return True


def add_catalog_column(catalog, column):
    columns = get_columns(catalog)
    if column in columns:
        logger.info("*** Column '%s' already in catalog '%s'"
                    % (column, catalog.id))
        return False
    add_column(catalog, column)
    logger.info("*** Added column '%s' to catalog '%s'"
                % (column, catalog.id))
    return True


def setup_catalog_mappings(portal, catalog_mappings=None):
    """Setup portal_type -> catalog mappings
    """
    logger.info("*** Setup Catalog Mappings ***")

    # allow add-ons to use this handler with own mappings
    if catalog_mappings is None:
        catalog_mappings = CATALOG_MAPPINGS

    at = api.get_tool("archetype_tool")
    for portal_type, catalogs in catalog_mappings:
        at.setCatalogsByType(portal_type, catalogs)


def setup_auditlog_catalog_mappings(portal):
    """Map auditlog catalog to all AT content types
    """
    at = api.get_tool("archetype_tool")
    pt = api.get_tool("portal_types")
    portal_types = pt.listContentTypes()

    # map all known AT types to the auditlog catalog
    auditlog_catalog = api.get_tool(AUDITLOG_CATALOG)
    for portal_type in portal_types:

        # Do not map DX types into archetypes tool
        fti = pt.getTypeInfo(portal_type)
        if isinstance(fti, DexterityFTI):
            continue

        catalogs = at.getCatalogsByType(portal_type)
        if auditlog_catalog not in catalogs:
            existing_catalogs = list(map(lambda c: c.getId(), catalogs))
            new_catalogs = existing_catalogs + [AUDITLOG_CATALOG]
            at.setCatalogsByType(portal_type, new_catalogs)
            logger.info("*** Adding catalog '{}' for '{}'".format(
                AUDITLOG_CATALOG, portal_type))


def setup_catalogs_order(portal):
    """Ensures the order of catalogs portal types are bound to is correct
    This is required because senaite.app.supermodel uses the first catalog
    the portal type is associated with when retrieving brains
    """
    logger.info("Setup Catalogs order ...")

    def sort_catalogs(id1, id2):
        if id1 == id2:
            return 0

        # Audit-log catalog is always the last!
        if id1 == AUDITLOG_CATALOG:
            return 1
        if id2 == AUDITLOG_CATALOG:
            return -1

        # Catalogs sorted, senaite_* always first
        senaite = map(lambda cat_id: cat_id.startswith("senaite_"), [id1, id2])
        if not all(senaite) and any(senaite):
            # Item starting with senaite always gets max priority
            if id1.startswith("senaite_"):
                return -1
            return 1

        if id1 < id2:
            return -1
        return 1

    at = api.get_tool("archetype_tool")
    for portal_type, catalogs in at.listCatalogs().items():
        sorted_catalogs = sorted(catalogs, cmp=sort_catalogs)
        at.setCatalogsByType(portal_type, sorted_catalogs)

    logger.info("Setup Catalogs order [DONE]")


def remove_default_content(portal):
    """Remove default Plone contents
    """
    logger.info("*** Remove Default Content ***")

    # Get the list of object ids for portal
    object_ids = portal.objectIds()
    delete_ids = filter(lambda id: id in object_ids, CONTENTS_TO_DELETE)
    if delete_ids:
        portal.manage_delObjects(ids=list(delete_ids))


def setup_content_structure(portal):
    """Install the base content structure
    """
    logger.info("*** Install SENAITE Content Types ***")
    _run_import_step(portal, "content")
    reindex_content_structure(portal)


def setup_form_controller_more_action(portal):
    """Install form controller actions for ported record widgets

    Code taken from Products.ATExtensions
    """
    logger.info("*** Install SENAITE Form Controller Actions ***")
    pfc = portal.portal_form_controller
    pfc.addFormValidators(
        "base_edit", "", "more", "")
    pfc.addFormAction(
        "base_edit", "success", "", "more", "traverse_to", "string:more_edit")
    pfc.addFormValidators(
        "atct_edit", "", "more", "",)
    pfc.addFormAction(
        "atct_edit", "success", "", "more", "traverse_to", "string:more_edit")


def _run_import_step(portal, name, profile="profile-bika.lims:default"):
    """Helper to install a GS import step from the given profile
    """
    logger.info("*** Running import step '{}' from profile '{}' ***"
                .format(name, profile))
    setup = portal.portal_setup
    setup.runImportStepFromProfile(profile, name)


def pre_install(portal_setup):
    """Runs berfore the first import step of the *default* profile

    This handler is registered as a *pre_handler* in the generic setup profile

    :param portal_setup: SetupTool
    """
    logger.info("SENAITE CORE pre-install handler")


def post_install(portal_setup):
    """Runs after the last import step of the *default* profile

    This handler is registered as a *post_handler* in the generic setup profile

    :param portal_setup: SetupTool
    """
    logger.info("SENAITE CORE post install handler [BEGIN]")

    # https://docs.plone.org/develop/addons/components/genericsetup.html#custom-installer-code-setuphandlers-py
    profile_id = PROFILE_ID
    context = portal_setup._getImportContext(profile_id)
    portal = context.getSite()

    # always apply the skins profile last to ensure our layers are first
    _run_import_step(portal, "skins", profile=profile_id)

    logger.info("SENAITE CORE post install handler [DONE]")


def setup_markup_schema(portal):
    """Sets the default and allowed markup schemas for RichText widgets
    """
    if not IMarkupSchema:
        return

    registry = getUtility(IRegistry, context=portal)
    settings = registry.forInterface(IMarkupSchema, prefix='plone')
    settings.default_type = u"text/html"
    settings.allowed_types = ("text/html", )
