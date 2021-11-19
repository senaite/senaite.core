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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from Acquisition import aq_base
from bika.lims import api
from bika.lims.setuphandlers import add_dexterity_portal_items
from bika.lims.setuphandlers import add_dexterity_setup_items
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
from senaite.core.api.catalog import get_columns
from senaite.core.api.catalog import get_indexes
from senaite.core.api.catalog import reindex_index
from senaite.core.catalog import AUDITLOG_CATALOG
from senaite.core.catalog import AnalysisCatalog
from senaite.core.catalog import AuditlogCatalog
from senaite.core.catalog import AutoImportLogCatalog
from senaite.core.catalog import ReportCatalog
from senaite.core.catalog import SampleCatalog
from senaite.core.catalog import SenaiteCatalog
from senaite.core.catalog import SetupCatalog
from senaite.core.catalog import WorksheetCatalog
from senaite.core.config import PROFILE_ID
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
    SampleCatalog,
    SenaiteCatalog,
    SetupCatalog,
    WorksheetCatalog,
    ReportCatalog,
)

INDEXES = (
    # catalog, id, indexed attribute, type
    ("portal_catalog", "Analyst", "", "FieldIndex"),
    ("portal_catalog", "analysisRequestTemplates", "", "FieldIndex"),
    ("portal_catalog", "getFullname", "", "FieldIndex"),
    ("portal_catalog", "getName", "", "FieldIndex"),
    ("portal_catalog", "getParentUID", "", "FieldIndex"),
    ("portal_catalog", "getUsername", "", "FieldIndex"),
    ("portal_catalog", "is_active", "", "BooleanIndex"),
    ("portal_catalog", "path", "getPhysicalPath", "ExtendedPathIndex"),
    ("portal_catalog", "review_state", "", "FieldIndex"),
    ("portal_catalog", "sample_uid", "", "KeywordIndex"),
    ("portal_catalog", "title", "", "FieldIndex"),
)

COLUMNS = (
    # catalog, column name
    ("portal_catalog", "analysisRequestTemplates"),
    ("portal_catalog", "review_state"),
    ("portal_catalog", "getClientID"),
    ("portal_catalog", "Analyst"),
)

CATALOG_MAPPINGS = (
    # portal_type, catalog_ids
    ("ARTemplate", ["senaite_catalog_setup", "portal_catalog"]),
    ("AnalysisCategory", ["senaite_catalog_setup", "portal_catalog"]),
    ("AnalysisProfile", ["senaite_catalog_setup", "portal_catalog"]),
    ("AnalysisService", ["senaite_catalog_setup", "portal_catalog"]),
    ("AnalysisSpec", ["senaite_catalog_setup", "portal_catalog"]),
    ("Attachment", ["senaite_catalog", "portal_catalog"]),
    ("AttachmentType", ["senaite_catalog_setup", "portal_catalog"]),
    ("Batch", ["senaite_catalog", "portal_catalog"]),
    ("BatchLabel", ["senaite_catalog_setup", "portal_catalog"]),
    ("Calculation", ["senaite_catalog_setup", "portal_catalog"]),
    ("Container", ["senaite_catalog_setup", "portal_catalog"]),
    ("ContainerType", ["senaite_catalog_setup", "portal_catalog"]),
    ("Department", ["senaite_catalog_setup", "portal_catalog"]),
    ("Instrument", ["senaite_catalog_setup", "portal_catalog"]),
    ("InstrumentType", ["senaite_catalog_setup", "portal_catalog"]),
    ("LabContact", ["senaite_catalog_setup", "portal_catalog"]),
    ("LabProduct", ["senaite_catalog_setup", "portal_catalog"]),
    ("Manufacturer", ["senaite_catalog_setup", "portal_catalog"]),
    ("Method", ["senaite_catalog_setup", "portal_catalog"]),
    ("Multifile", ["senaite_catalog_setup", "portal_catalog"]),
    ("Preservation", ["senaite_catalog_setup", "portal_catalog"]),
    ("ReferenceDefinition", ["senaite_catalog_setup", "portal_catalog"]),
    ("ReferenceSample", ["senaite_catalog", "portal_catalog"]),
    ("SampleCondition", ["senaite_catalog_setup", "portal_catalog"]),
    ("SampleMatrix", ["senaite_catalog_setup", "portal_catalog"]),
    ("SamplePoint", ["senaite_catalog_setup", "portal_catalog"]),
    ("SampleType", ["senaite_catalog_setup", "portal_catalog"]),
    ("SamplingDeviation", ["senaite_catalog_setup", "portal_catalog"]),
    ("StorageLocation", ["senaite_catalog_setup", "portal_catalog"]),
    ("SubGroup", ["senaite_catalog_setup", "portal_catalog"]),
    ("Supplier", ["senaite_catalog_setup", "portal_catalog"]),
    ("WorksheetTemplate", ["senaite_catalog_setup", "portal_catalog"]),
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
    setup_core_catalogs(portal)
    setup_other_catalogs(portal)
    setup_catalog_mappings(portal)
    setup_auditlog_catalog_mappings(portal)
    setup_content_structure(portal)
    add_dexterity_portal_items(portal)
    add_dexterity_setup_items(portal)

    # Set CMF Form actions
    setup_form_controller_actions(portal)
    setup_form_controller_more_action(portal)

    # Setup markup default and allowed schemas
    setup_markup_schema(portal)

    logger.info("SENAITE CORE install handler [DONE]")


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
    logger.info("SENAITE CORE pre-install handler [BEGIN]")

    # https://docs.plone.org/develop/addons/components/genericsetup.html#custom-installer-code-setuphandlers-py
    profile_id = PROFILE_ID
    context = portal_setup._getImportContext(profile_id)
    portal = context.getSite()  # noqa

    logger.info("SENAITE CORE pre-install handler [DONE]")


def post_install(portal_setup):
    """Runs after the last import step of the *default* profile

    This handler is registered as a *post_handler* in the generic setup profile

    :param portal_setup: SetupTool
    """
    logger.info("SENAITE CORE post install handler [BEGIN]")

    # https://docs.plone.org/develop/addons/components/genericsetup.html#custom-installer-code-setuphandlers-py
    profile_id = PROFILE_ID
    context = portal_setup._getImportContext(profile_id)
    portal = context.getSite()  # noqa

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
